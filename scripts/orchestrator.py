#!/usr/bin/env python3
"""
🜏 Lipro-Hass 重构主控代理 (Orchestrator)

负责协调多个子代理并行执行重构任务，监控进度，处理冲突，生成报告。
"""

import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("docs/refactoring/orchestrator.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("orchestrator")


class AgentStatus(Enum):
    """代理状态"""
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """任务定义"""
    agent_id: str
    task_name: str
    phase: str
    priority: str
    dependencies: list[str]
    task_file: Path
    status: TaskStatus = TaskStatus.PENDING
    assigned_at: float | None = None
    completed_at: float | None = None
    error: str | None = None
    checkpoints_completed: int = 0
    total_checkpoints: int = 0


@dataclass
class Agent:
    """代理状态"""
    agent_id: str
    agent_name: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Task | None = None
    last_heartbeat: float = field(default_factory=time.time)
    progress: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0


class FileLockManager:
    """文件锁管理器"""

    def __init__(self, lock_file: Path):
        self.lock_file = lock_file
        self.locks: dict[str, str] = {}
        self._lock = asyncio.Lock()

    async def load_locks(self) -> dict[str, str]:
        """加载锁文件"""
        if self.lock_file.exists():
            return json.loads(self.lock_file.read_text())
        return {}

    async def save_locks(self, locks: dict[str, str]) -> None:
        """保存锁文件"""
        self.lock_file.write_text(json.dumps(locks, indent=2))

    async def acquire_lock(self, agent_id: str, file_path: str) -> bool:
        """获取文件锁"""
        async with self._lock:
            locks = await self.load_locks()

            if file_path in locks:
                current_owner = locks[file_path]
                if current_owner != agent_id:
                    logger.warning(
                        f"File {file_path} is locked by {current_owner}, "
                        f"{agent_id} cannot acquire"
                    )
                    return False

            locks[file_path] = agent_id
            await self.save_locks(locks)
            logger.info(f"{agent_id} acquired lock on {file_path}")
            return True

    async def release_lock(self, agent_id: str, file_path: str) -> None:
        """释放文件锁"""
        async with self._lock:
            locks = await self.load_locks()
            if locks.get(file_path) == agent_id:
                del locks[file_path]
                await self.save_locks(locks)
                logger.info(f"{agent_id} released lock on {file_path}")

    async def release_all_locks(self, agent_id: str) -> None:
        """释放代理的所有锁"""
        async with self._lock:
            locks = await self.load_locks()
            files_to_release = [
                file_path
                for file_path, owner in locks.items()
                if owner == agent_id
            ]
            for file_path in files_to_release:
                del locks[file_path]
            await self.save_locks(locks)
            if files_to_release:
                logger.info(f"{agent_id} released {len(files_to_release)} locks")


class RefactorOrchestrator:
    """重构主控代理"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.tasks_dir = base_dir / "docs/refactoring/tasks"
        self.checkpoints_dir = base_dir / "docs/refactoring/checkpoints"
        self.status_file = base_dir / "docs/refactoring/STATUS.md"
        self.lock_file = base_dir / "docs/refactoring/locks.json"

        self.agents: dict[str, Agent] = {}
        self.tasks: list[Task] = []
        self.completed_tasks: list[Task] = []
        self.failed_tasks: list[Task] = []

        self.file_lock_manager = FileLockManager(self.lock_file)
        self.start_time = time.time()

    async def initialize(self) -> None:
        """初始化主控代理"""
        logger.info("🜏 Initializing Refactor Orchestrator...")

        # 创建目录
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

        # 加载任务
        await self.load_tasks()

        # 初始化代理
        self.initialize_agents()

        logger.info(f"Loaded {len(self.tasks)} tasks, {len(self.agents)} agents")

    def initialize_agents(self) -> None:
        """初始化代理"""
        agent_configs = [
            ("agent-1", "Exception Refactor Agent"),
            ("agent-2", "Type Safety Agent"),
            ("agent-3", "Architecture Refactor Agent"),
            ("agent-4", "Device Model Refactor Agent"),
            ("agent-5", "MQTT Client Refactor Agent"),
            ("agent-6", "Testing & Validation Agent"),
        ]

        for agent_id, agent_name in agent_configs:
            self.agents[agent_id] = Agent(agent_id=agent_id, agent_name=agent_name)

    async def load_tasks(self) -> None:
        """加载所有任务"""
        task_files = sorted(self.tasks_dir.glob("agent-*.json"))

        for task_file in task_files:
            try:
                task_data = json.loads(task_file.read_text())
                task = Task(
                    agent_id=task_data["agent_id"],
                    task_name=task_data["task_name"],
                    phase=task_data["phase"],
                    priority=task_data["priority"],
                    dependencies=task_data["dependencies"],
                    task_file=task_file,
                    total_checkpoints=len(task_data["checkpoints"]),
                )
                self.tasks.append(task)
                logger.info(f"Loaded task: {task.task_name} ({task.agent_id})")
            except Exception as err:
                logger.error(f"Failed to load task {task_file}: {err}")

    def get_ready_tasks(self) -> list[Task]:
        """获取可执行的任务（依赖已满足）"""
        ready_tasks = []

        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue

            # 检查依赖
            dependencies_met = all(
                any(
                    t.agent_id == dep and t.status == TaskStatus.COMPLETED
                    for t in self.completed_tasks
                )
                for dep in task.dependencies
            )

            if dependencies_met or not task.dependencies:
                ready_tasks.append(task)

        # 按优先级排序
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        ready_tasks.sort(key=lambda t: priority_order.get(t.priority, 99))

        return ready_tasks

    async def assign_task(self, agent_id: str, task: Task) -> None:
        """分配任务给代理"""
        agent = self.agents[agent_id]
        agent.status = AgentStatus.WORKING
        agent.current_task = task

        task.status = TaskStatus.ASSIGNED
        task.assigned_at = time.time()

        logger.info(f"✅ Assigned task '{task.task_name}' to {agent_id}")

        # 通知代理（实际实现中可以通过消息队列、文件监听等方式）
        # 这里简化为日志记录
        logger.info(
            f"📋 {agent_id} should execute: "
            f"python scripts/agent_worker.py --agent-id {agent_id} "
            f"--task-file {task.task_file}"
        )

    async def monitor_progress(self) -> None:
        """监控所有代理进度"""
        logger.info("🔍 Starting progress monitoring...")

        while self.has_active_tasks():
            for agent_id, agent in self.agents.items():
                if agent.status != AgentStatus.WORKING:
                    continue

                # 检查心跳
                if time.time() - agent.last_heartbeat > 300:  # 5 分钟无响应
                    logger.warning(f"⚠️ {agent_id} timeout (no heartbeat)")
                    await self.handle_agent_timeout(agent_id)
                    continue

                # 检查检查点进度
                checkpoints = await self.read_checkpoints(agent_id)
                if agent.current_task:
                    agent.current_task.checkpoints_completed = len(checkpoints)
                    agent.progress = (
                        len(checkpoints) / agent.current_task.total_checkpoints
                        if agent.current_task.total_checkpoints > 0
                        else 0.0
                    )

                # 检查任务完成
                if agent.current_task and agent.progress >= 1.0:
                    await self.handle_task_completed(agent_id)

            # 更新监控面板
            await self.update_dashboard()

            # 分配新任务
            await self.assign_ready_tasks()

            await asyncio.sleep(30)  # 每 30 秒检查一次

        logger.info("✅ All tasks completed or failed")

    async def read_checkpoints(self, agent_id: str) -> list[dict[str, Any]]:
        """读取代理的检查点"""
        agent_checkpoint_dir = self.checkpoints_dir / agent_id
        if not agent_checkpoint_dir.exists():
            return []

        checkpoints = []
        for checkpoint_file in sorted(agent_checkpoint_dir.glob("cp-*.json")):
            try:
                checkpoint = json.loads(checkpoint_file.read_text())
                if checkpoint.get("status") == "success":
                    checkpoints.append(checkpoint)
            except Exception as err:
                logger.error(f"Failed to read checkpoint {checkpoint_file}: {err}")

        return checkpoints

    async def handle_agent_timeout(self, agent_id: str) -> None:
        """处理代理超时"""
        agent = self.agents[agent_id]
        agent.status = AgentStatus.TIMEOUT

        if agent.current_task:
            agent.current_task.status = TaskStatus.FAILED
            agent.current_task.error = "Agent timeout (no heartbeat)"
            self.failed_tasks.append(agent.current_task)
            agent.tasks_failed += 1

        # 释放所有锁
        await self.file_lock_manager.release_all_locks(agent_id)

        logger.error(f"❌ {agent_id} marked as timeout")

    async def handle_task_completed(self, agent_id: str) -> None:
        """处理任务完成"""
        agent = self.agents[agent_id]

        if agent.current_task:
            agent.current_task.status = TaskStatus.COMPLETED
            agent.current_task.completed_at = time.time()
            self.completed_tasks.append(agent.current_task)
            self.tasks.remove(agent.current_task)
            agent.tasks_completed += 1

            duration = (
                agent.current_task.completed_at - agent.current_task.assigned_at
                if agent.current_task.assigned_at
                else 0
            )

            logger.info(
                f"✅ {agent_id} completed task '{agent.current_task.task_name}' "
                f"in {duration:.1f}s"
            )

        agent.status = AgentStatus.IDLE
        agent.current_task = None
        agent.progress = 0.0

        # 释放所有锁
        await self.file_lock_manager.release_all_locks(agent_id)

    async def assign_ready_tasks(self) -> None:
        """分配就绪的任务"""
        ready_tasks = self.get_ready_tasks()
        idle_agents = [
            agent_id
            for agent_id, agent in self.agents.items()
            if agent.status == AgentStatus.IDLE
        ]

        for task in ready_tasks:
            if task.agent_id in idle_agents:
                await self.assign_task(task.agent_id, task)
                idle_agents.remove(task.agent_id)

            if not idle_agents:
                break

    def has_active_tasks(self) -> bool:
        """是否有活跃任务"""
        return bool(
            self.tasks
            or any(agent.status == AgentStatus.WORKING for agent in self.agents.values())
        )

    async def update_dashboard(self) -> None:
        """更新监控面板"""
        report = self.generate_status_report()
        self.status_file.write_text(report)

    def generate_status_report(self) -> str:
        """生成状态报告"""
        lines = []
        lines.append("# 🜏 重构进度监控\n")
        lines.append(f"**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 总体进度
        total_tasks = len(self.completed_tasks) + len(self.tasks) + len(self.failed_tasks)
        if total_tasks > 0:
            progress = len(self.completed_tasks) / total_tasks * 100
            lines.append(
                f"**总体进度**: {progress:.1f}% "
                f"({len(self.completed_tasks)}/{total_tasks})\n"
            )

        # 代理状态
        lines.append("\n## 代理状态\n")
        for agent_id, agent in sorted(self.agents.items()):
            emoji = {
                AgentStatus.IDLE: "⚪",
                AgentStatus.WORKING: "🟢",
                AgentStatus.COMPLETED: "✅",
                AgentStatus.FAILED: "🔴",
                AgentStatus.TIMEOUT: "⏱️",
            }.get(agent.status, "❓")

            lines.append(f"- {emoji} **{agent.agent_name}** ({agent_id}): {agent.status.value}")

            if agent.current_task:
                lines.append(
                    f" - 任务: {agent.current_task.task_name} "
                    f"({agent.progress:.0%}, "
                    f"{agent.current_task.checkpoints_completed}/"
                    f"{agent.current_task.total_checkpoints} checkpoints)"
                )

            lines.append(
                f" - 统计: {agent.tasks_completed} 完成, "
                f"{agent.tasks_failed} 失败\n"
            )

        # 待执行任务
        if self.tasks:
            lines.append("\n## 待执行任务\n")
            for task in self.tasks[:5]:
                lines.append(
                    f"- ⏳ {task.task_name} ({task.agent_id}) - "
                    f"Phase {task.phase}, {task.priority}\n"
                )

        # 最近完成
        if self.completed_tasks:
            lines.append("\n## 最近完成\n")
            for task in self.completed_tasks[-5:]:
                duration = (
                    task.completed_at - task.assigned_at
                    if task.completed_at and task.assigned_at
                    else 0
                )
                lines.append(
                    f"- ✅ {task.task_name} ({task.agent_id}) - "
                    f"{duration:.1f}s\n"
                )

        # 失败任务
        if self.failed_tasks:
            lines.append("\n## ⚠️ 失败任务\n")
            for task in self.failed_tasks:
                lines.append(
                    f"- ❌ {task.task_name} ({task.agent_id}): "
                    f"{task.error or 'Unknown error'}\n"
                )

        # 运行时间
        runtime = time.time() - self.start_time
        lines.append(f"\n**运行时间**: {runtime / 3600:.1f} 小时\n")

        return "".join(lines)

    async def generate_final_report(self) -> str:
        """生成最终报告"""
        lines = []
        lines.append("# 🜏 Lipro-Hass 重构完成报告\n")

        # 执行摘要
        lines.append("\n## 📊 执行摘要\n")
        end_time = time.time()
        duration = end_time - self.start_time

        lines.append(f"- **开始时间**: {datetime.fromtimestamp(self.start_time)}\n")
        lines.append(f"- **结束时间**: {datetime.fromtimestamp(end_time)}\n")
        lines.append(f"- **总耗时**: {duration / 3600:.1f} 小时\n")
        lines.append(f"- **参与代理**: {len(self.agents)}\n")
        lines.append(f"- **完成任务**: {len(self.completed_tasks)}\n")
        lines.append(f"- **失败任务**: {len(self.failed_tasks)}\n")

        # 各代理贡献
        lines.append("\n## 🏆 代理贡献\n")
        for agent_id, agent in sorted(self.agents.items()):
            lines.append(f"### {agent.agent_name} ({agent_id})\n")
            lines.append(f"- **完成任务**: {agent.tasks_completed}\n")
            lines.append(f"- **失败任务**: {agent.tasks_failed}\n")

        return "".join(lines)

    async def run(self) -> None:
        """运行主控代理"""
        await self.initialize()
        await self.assign_ready_tasks()
        await self.monitor_progress()

        # 生成最终报告
        final_report = await self.generate_final_report()
        final_report_file = self.base_dir / "docs/refactoring/FINAL_REPORT.md"
        final_report_file.write_text(final_report)

        logger.info(f"✅ Refactoring completed! Final report: {final_report_file}")


async def main() -> None:
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Lipro-Hass Refactor Orchestrator")
    parser.add_argument(
        "command",
        choices=["init", "start", "monitor", "retry-failed"],
        help="Command to execute",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Base directory (default: current directory)",
    )

    args = parser.parse_args()

    orchestrator = RefactorOrchestrator(args.base_dir)

    if args.command == "init":
        await orchestrator.initialize()
        logger.info("✅ Orchestrator initialized")

    elif args.command == "start":
        await orchestrator.run()

    elif args.command == "monitor":
        await orchestrator.initialize()
        while True:
            await orchestrator.update_dashboard()
            await asyncio.sleep(60)

    elif args.command == "retry-failed":
        await orchestrator.initialize()
        # 重新分配失败任务
        for task in orchestrator.failed_tasks:
            task.status = TaskStatus.PENDING
            task.error = None
            orchestrator.tasks.append(task)
        orchestrator.failed_tasks.clear()
        await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(main())
