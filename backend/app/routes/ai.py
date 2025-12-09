from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.ai_service import ai_service
from app.database import get_db
from app.models import User
from app.auth import get_current_user
import json

router = APIRouter(prefix="/ai", tags=["ai"])


class AIProcessRequest(BaseModel):
    text: str
    note_id: str | None = None


async def generate_stream(ai_service_instance, text: str, note_id: str | None):
    """生成流式响应"""
    try:
        print("=" * 60)
        print("【AI处理请求】")
        print(f"笔记ID: {note_id}")
        print(f"处理前文本长度: {len(text)} 字符")
        print(f"处理前文本内容（前200字符）: {text[:200]}")
        print("=" * 60)
        
        chunk_count = 0
        total_content = ""
        async for chunk in ai_service_instance.process_text_stream(text, note_id):
            # 使用Server-Sent Events格式
            if chunk:  # 确保chunk不为空
                total_content += chunk
                data = json.dumps({"content": chunk}, ensure_ascii=False)
                yield f"data: {data}\n\n"
                chunk_count += 1
        
        print("=" * 60)
        print("【AI处理完成】")
        print(f"共处理 {chunk_count} 个chunk")
        print(f"处理后文本长度: {len(total_content)} 字符")
        print(f"处理后文本内容（前200字符）: {total_content[:200]}")
        print("=" * 60)
        
        # 如果没有收到任何chunk，可能是API调用失败
        if chunk_count == 0:
            error_msg = json.dumps({"error": "AI服务未返回任何内容，请检查API配置和网络连接"}, ensure_ascii=False)
            yield f"data: {error_msg}\n\n"
        
        yield "data: [DONE]\n\n"
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"流式处理错误: {error_detail}")
        error_data = json.dumps({"error": f"AI处理失败: {str(e)}"}, ensure_ascii=False)
        yield f"data: {error_data}\n\n"


@router.post("/process")
async def process_text(
    request: AIProcessRequest,
    current_user: User = Depends(get_current_user)
):
    """处理文本（流式响应）"""
    return StreamingResponse(
        generate_stream(ai_service, request.text, request.note_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

