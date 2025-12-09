from openai import OpenAI
from app.config import settings
from typing import AsyncGenerator
import asyncio
import concurrent.futures


class AIService:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.api_base = settings.openai_api_base
        self._client = None
    
    @property
    def client(self):
        """延迟初始化客户端，避免模块加载时的错误"""
        if self._client is None:
            client_kwargs = {"api_key": self.api_key}
            if self.api_base:
                client_kwargs["base_url"] = self.api_base
            self._client = OpenAI(**client_kwargs)
        return self._client

    async def process_text_stream(
        self, text: str, note_id: str | None = None
    ) -> AsyncGenerator[str, None]:
        """
        流式处理文本，使用OpenAI API
        """
        try:
            # 构建提示词
            prompt = f"""请帮我润色和扩展以下文本，使其更加清晰、有条理和完整。保持原意，但可以适当扩展和优化表达：

{text}

请直接输出润色后的内容，不要添加额外的说明或标记。"""

            # OpenAI Python SDK 的流式调用是同步的，需要在线程池中运行
            import concurrent.futures
            
            def create_stream():
                try:
                    print(f"调用AI API - 模型: {settings.openai_model}, Base URL: {settings.openai_api_base or '默认'}")
                    response = self.client.chat.completions.create(
                        model=settings.openai_model,  # 使用配置的模型名称
                        messages=[
                            {"role": "system", "content": "你是一个专业的文本润色助手，擅长改进文本的表达和结构。"},
                            {"role": "user", "content": prompt}
                        ],
                        stream=True,
                        temperature=0.7,
                        max_tokens=2000
                    )
                    print("AI API调用成功，开始流式处理")
                    return response
                except Exception as e:
                    print(f"AI API调用失败: {e}")
                    import traceback
                    traceback.print_exc()
                    raise
            
            # 在线程池中执行同步调用
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                stream = await loop.run_in_executor(executor, create_stream)
                
                # 流式返回内容
                total_content = ""
                chunk_index = 0
                has_finished = False
                
                for chunk in stream:
                    try:
                        chunk_index += 1
                        
                        # 检查是否有finish_reason（流结束标记）
                        if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                            choice = chunk.choices[0]
                            
                            # 检查finish_reason，但不立即退出，先处理完当前chunk
                            if hasattr(choice, 'finish_reason') and choice.finish_reason:
                                has_finished = True
                                print(f"检测到流结束标记: {choice.finish_reason}")
                            
                            # 处理delta内容
                            if hasattr(choice, 'delta'):
                                delta = choice.delta
                                if hasattr(delta, 'content') and delta.content:
                                    content = delta.content
                                    if content:  # 确保内容不为空
                                        total_content += content
                                        yield content
                                        # 让出控制权，避免阻塞
                                        await asyncio.sleep(0)
                            
                            # 如果已经结束，处理完当前chunk后退出
                            if has_finished:
                                print(f"流式处理完成，共处理 {chunk_index} 个chunk，总长度: {len(total_content)}")
                                break
                        else:
                            # 如果没有choices，可能是其他类型的chunk，继续处理
                            print(f"收到非标准chunk (索引 {chunk_index}): {type(chunk)}")
                            
                    except Exception as chunk_error:
                        # 记录chunk处理错误，但继续处理
                        print(f"处理chunk {chunk_index} 时出错: {chunk_error}")
                        import traceback
                        traceback.print_exc()
                        continue
                
                # 如果流自然结束（没有finish_reason），也记录
                if not has_finished:
                    print(f"流自然结束，共处理 {chunk_index} 个chunk，总长度: {len(total_content)}")
                
                if not total_content:
                    print("警告：未收到任何内容，可能是API响应格式不兼容")
                    yield "⚠️ AI服务未返回内容，请检查API配置或稍后重试。"
                elif len(total_content) < 10:
                    print(f"警告：返回内容过短 ({len(total_content)} 字符)，可能是API响应异常")
                    yield f"{total_content}\n\n⚠️ 注意：返回内容可能不完整，请重试。"

        except Exception as e:
            error_msg = f"AI处理错误: {str(e)}"
            yield error_msg
            raise


ai_service = AIService()

