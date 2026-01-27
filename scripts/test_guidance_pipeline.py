"""
测试 AI 引擎到前端 3D Widget 的数据通道
验证第一条"辅助线"能否正确生成和传递
"""
import httpx
import asyncio
import json


async def test_ai_engine_health():
    """测试 AI 引擎健康状态"""
    print("\n" + "="*60)
    print("🧪 测试 1: AI 引擎健康检查")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8001/api/health")
            print(f"✅ AI 引擎状态: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ AI 引擎无法访问: {e}")
            return False


async def test_backend_health():
    """测试后端服务健康状态"""
    print("\n" + "="*60)
    print("🧪 测试 2: 后端服务健康检查")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/api/health")
            print(f"✅ 后端服务状态: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ 后端服务无法访问: {e}")
            return False


async def test_guidance_generation_direct():
    """测试直接调用 AI 引擎生成导学步骤"""
    print("\n" + "="*60)
    print("🧪 测试 3: AI 引擎生成导学步骤（直接调用）")
    print("="*60)
    
    payload = {
        "user_id": "test_user",
        "content": "求解三角形 ABC 的面积，已知 AB=5, BC=6, AC=7"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "http://localhost:8001/api/guidance/generate",
                json=payload
            )
            
            result = response.json()
            print(f"✅ 返回数据结构:")
            print(f"   • session_id: {result.get('session_id')}")
            print(f"   • task_id: {result.get('task_id')}")
            print(f"   • 步骤数量: {len(result.get('steps', []))}")
            
            # 检查是否有几何数据
            for i, step in enumerate(result.get('steps', []), 1):
                print(f"\n   步骤 {i}: {step.get('title')}")
                print(f"      - step_id: {step.get('step_id')}")
                print(f"      - type: {step.get('type')}")
                
                if step.get('geometry'):
                    geometry = step['geometry']
                    objects = geometry.get('objects', [])
                    print(f"      - ✨ 包含 {len(objects)} 个几何对象:")
                    
                    for obj in objects:
                        obj_type = obj.get('type')
                        label = obj.get('label', '无标签')
                        coords_count = len(obj.get('coords', []))
                        print(f"         • {obj_type}: {label} ({coords_count} 个顶点)")
            
            return result
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            return None


async def test_guidance_via_backend():
    """测试通过后端服务调用生成导学步骤"""
    print("\n" + "="*60)
    print("🧪 测试 4: 通过后端服务生成导学步骤（完整链路）")
    print("="*60)
    
    payload = {
        "user_id": "test_user_backend",
        "content": "如何证明三角形内角和为 180 度",
        "mode": "text"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/capture/text",
                json=payload
            )
            
            result = response.json()
            print(f"✅ 后端返回数据:")
            print(f"   • session_id: {result.get('session_id')}")
            print(f"   • task_id: {result.get('task_id')}")
            print(f"   • 步骤数量: {len(result.get('steps', []))}")
            
            # 验证几何数据
            has_geometry = False
            for step in result.get('steps', []):
                if step.get('geometry'):
                    has_geometry = True
                    geometry = step['geometry']
                    objects = geometry.get('objects', [])
                    
                    print(f"\n   ✅ 发现几何步骤: {step.get('title')}")
                    print(f"      包含 {len(objects)} 个几何对象")
                    
                    # 验证数据格式是否符合前端 ThreeDVisualizationWidget 的要求
                    for obj in objects:
                        assert 'type' in obj, "缺少 type 字段"
                        assert 'coords' in obj, "缺少 coords 字段"
                        assert obj['type'] in ['line', 'point', 'face', 'polygon'], f"未知类型: {obj['type']}"
                        
                        coords = obj['coords']
                        assert isinstance(coords, list), "coords 必须是数组"
                        assert len(coords) > 0, "coords 不能为空"
                        
                        # 验证每个顶点是 [x, y, z]
                        for coord in coords:
                            assert isinstance(coord, list), "每个顶点必须是数组"
                            assert len(coord) == 3, "每个顶点必须有 x, y, z 三个坐标"
                    
                    print("      ✅ 数据格式验证通过，前端可以直接渲染！")
            
            if not has_geometry:
                print("\n   ⚠️  警告: 没有找到几何数据，可能不会显示 3D 演示")
            
            return result
            
        except Exception as e:
            print(f"❌ 后端调用失败: {e}")
            import traceback
            traceback.print_exc()
            return None


async def test_reasoning_visual_commands():
    """测试 AI 推理接口返回的 visual_commands（几何辅助线闭环）"""
    print("\n" + "="*60)
    print("🧪 测试 5: 几何推理 visual_commands")
    print("="*60)

    payload = {
        "user_id": "test_visual_geometry",
        "query": "已知三角形 ABC，连接 AC 的中点 D 到 B，求证明相关几何关系。",
        "domain": "geometry",
        "context": [],
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                "http://localhost:8001/api/reasoning/process",
                json=payload,
            )

            result = response.json()
            print(f"✅ 推理答案: {result.get('answer')}")

            commands = result.get("visual_commands", [])
            print(f"   • visual_commands 数量: {len(commands)}")

            for i, cmd in enumerate(commands, 1):
                print(f"\n   指令 {i}:")
                print(f"      type: {cmd.get('type')}")
                if cmd.get('type') == 'draw_line':
                    print(
                        f"      from: {cmd.get('from')}  ->  to: {cmd.get('to')}  color: {cmd.get('color')}"
                    )
                if cmd.get('type') == 'highlight_angle':
                    print(f"      points: {cmd.get('points')}")

            if not commands:
                print("\n   ⚠️  未返回 visual_commands，请检查 ReasoningEngine._generate_visual_commands 逻辑。")

            return result
        except Exception as e:
            print(f"❌ visual_commands 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return None


async def test_follow_up():
    """测试追问功能"""
    print("\n" + "="*60)
    print("🧪 测试 5: 追问某一步骤")
    print("="*60)
    
    # 先生成初始导学
    initial_payload = {
        "user_id": "test_user_followup",
        "content": "求圆的面积",
        "mode": "text"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 第一次请求
            response1 = await client.post(
                "http://localhost:8000/api/capture/text",
                json=initial_payload
            )
            
            result1 = response1.json()
            session_id = result1.get('session_id')
            first_step_id = result1['steps'][0]['step_id'] if result1.get('steps') else None
            
            print(f"✅ 初始会话创建: {session_id}")
            print(f"   第一个步骤: {first_step_id}")
            
            # 针对第一个步骤追问
            if first_step_id:
                followup_payload = {
                    "session_id": session_id,
                    "user_id": "test_user_followup",
                    "content": "我不太明白这一步，能详细讲讲吗？",
                    "step_id": first_step_id
                }
                
                response2 = await client.post(
                    "http://localhost:8000/api/session/message",
                    json=followup_payload
                )
                
                result2 = response2.json()
                print(f"\n✅ 追问返回:")
                print(f"   • 新步骤数量: {len(result2.get('steps', []))}")
                
                for step in result2.get('steps', []):
                    if 'detail' in step['step_id'] or step.get('type') == 'detail':
                        print(f"   • 🎯 找到详细讲解步骤: {step.get('title')}")
                
                return True
            
        except Exception as e:
            print(f"❌ 追问测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """运行所有测试"""
    print("\n" + "🎯 " * 20)
    print("开始测试 AI 引擎到前端 3D Widget 的完整数据通道")
    print("🎯 " * 20)
    
    # 1. 健康检查
    ai_ok = await test_ai_engine_health()
    backend_ok = await test_backend_health()
    
    if not (ai_ok and backend_ok):
        print("\n❌ 服务未启动，请先运行:")
        print("   python scripts/start_services.py")
        print("   或")
        print("   powershell scripts/start_services.ps1")
        return
    
    # 2. 测试 AI 引擎直接调用
    await test_guidance_generation_direct()
    
    # 3. 测试完整链路（模拟前端调用）
    result = await test_guidance_via_backend()
    
    # 4. 测试追问
    await test_follow_up()

    # 5. 测试几何 visual_commands
    await test_reasoning_visual_commands()
    
    print("\n" + "="*60)
    print("🎉 测试完成！")
    print("="*60)
    print("\n📱 下一步:")
    print("   1. 启动 Flutter 前端")
    print("   2. 在「多模态采集」页面输入文本问题")
    print("   3. 查看生成的导学步骤")
    print("   4. 确认带几何数据的步骤下方出现 3D 演示")
    print("   5. 拖动 3D 视图验证交互")
    print("   6. 点击「追问」按钮测试分步引导")
    print("\n✨ 如果一切正常，你应该能看到第一条\"辅助线 AC\"在 3D 空间中旋转！")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
