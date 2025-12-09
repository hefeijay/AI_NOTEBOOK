from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
from app.database import SessionLocal
from app.models import Note


class ConnectionManager:
    def __init__(self):
        # 存储每个笔记的连接
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, note_id: str):
        await websocket.accept()
        if note_id not in self.active_connections:
            self.active_connections[note_id] = set()
        self.active_connections[note_id].add(websocket)

    def disconnect(self, websocket: WebSocket, note_id: str):
        if note_id in self.active_connections:
            self.active_connections[note_id].discard(websocket)
            if not self.active_connections[note_id]:
                del self.active_connections[note_id]

    async def broadcast_to_note(self, note_id: str, message: dict):
        """向特定笔记的所有连接广播消息"""
        if note_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[note_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            
            # 清理断开的连接
            for conn in disconnected:
                self.disconnect(conn, note_id)

    async def broadcast_to_all(self, message: dict):
        """向所有连接广播消息"""
        all_connections = set()
        for connections in self.active_connections.values():
            all_connections.update(connections)
        
        disconnected = set()
        for connection in all_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.add(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            for note_id, connections in list(self.active_connections.items()):
                if conn in connections:
                    self.disconnect(conn, note_id)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, note_id: str | None = None):
    """WebSocket端点处理"""
    await manager.connect(websocket, note_id or "global")
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                elif msg_type == "note_update":
                    # 更新数据库
                    db = SessionLocal()
                    try:
                        note_data = message.get("payload", {})
                        note = db.query(Note).filter(Note.id == note_data.get("id")).first()
                        if note:
                            if "title" in note_data:
                                note.title = note_data["title"]
                            if "content" in note_data:
                                note.content = note_data["content"]
                            db.commit()
                            
                            # 广播更新
                            await manager.broadcast_to_note(
                                note_data.get("id"),
                                {
                                    "type": "note_update",
                                    "payload": note.to_dict()
                                }
                            )
                    finally:
                        db.close()
                elif msg_type == "note_create":
                    note_data = message.get("payload", {})
                    await manager.broadcast_to_all({
                        "type": "note_create",
                        "payload": note_data
                    })
                elif msg_type == "note_delete":
                    payload = message.get("payload", {})
                    note_id_to_delete = payload.get("id")
                    await manager.broadcast_to_all({
                        "type": "note_delete",
                        "payload": payload
                    })
            except json.JSONDecodeError:
                # 忽略无效的JSON消息
                continue
            except Exception as e:
                # 处理其他错误
                print(f"WebSocket处理错误: {e}")
                continue
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket, note_id or "global")

