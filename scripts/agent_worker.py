#!/usr/bin/env python3
"""
🜏 Lipro-Hass 重构子代理工作器 (Agent Worker)

读取任务定义，执行检查点，验证结果，提交代码，报告进度。
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("agent_worker")


@dataclass
class Checkpoint:
    """检查点定义"""
    id: str
    description: str
    tasks: list[str]
    files: list[str]
    validation: dict[str, str]
    commit_message: str


@dataclass
class TaskDefinition:
    """任务定义"""
    agent_id: str
    agent_name: str
    task_name: str
    phase: str
    priority: str
    dependencies: list[str]
    description: str
    input_files: list[str]
    output_branch: str
    base_branch: str
    checkpoints: list[Checkpoint]
    success_criteria: dict[str, Any]
    retry_policy: dict[str, Any]
    failure_handling: dict[str, str]
    reporting: dict[str, Any]


class RetryPolicy:
    """重试策略"""

    def __init__(self, max_retries: int = 3, base_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def retry_with_backoff(
        self,
        func: callable,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """指数退避重试"""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as err:
                if attempt == self.max_retries - 1:
                    raise

                delay = self.base_delay * (2 ** attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {err}. "
                    f"Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)


class AgentWorker:
    """子代理工作器"""

    def __init__(
        self,
        agent_id: str,
        task_file: Path,
        base_dir: Path,
        recover_from_checkpoint: bool = False,
    ):
        self.agent_id = agent_id
        self.task_file = task_file
        self.base_dir = base_dir
        self.recover_from_checkpoint = recover_from_checkpoint

        self.checkpoint_dir = base_dir / "docs/refactoring/checkpoints" / agent_id
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.task: TaskDefinition | None = None
        self.retry_policy: RetryPolicy | None = None

        # 添加日志文件处理器
        log_file = base_dir / f"docs/refactoring/{agent_id}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(file_handler)

    async def load_task(self) -> None:
        """加载任务定义"""
        logger.info(f"Loading task from {self.task_file}")

        task_data = json.loads(self.task_file.read_text())

        # 解析检查点
        checkpoints = [
            Checkpoint(
                id=cp["id"],
                description=cp["description"],
                tasks=cp["tasks"],
                files=cp["files"],
                validation=cp["validation"],
                commit_message=cp["commit_message"],
            )
            for cp in task_data["checkpoints"]
        ]

        self.task = TaskDefinition(
            agent_id=task_data["agent_id"],
            agent_name=task_data["agent_name"],
            task_name=task_data["task_name"],
            phase=task_data["phase"],
            priority=task_data["priority"],
            dependencies=task_data["dependencies"],
            description=task_data["description"],
            input_files=task_data["input_files"],
            output_branch=task_data["output_branch"],
            base_branch=task_data["base_branch"],
            checkpoints=checkpoints,
            success_criteria=task_data["success_criteria"],
            retry_policy=task_data["retry_policy"],
            failure_handling=task_data["failure_handling"],
            reporting=task_data["reporting"],
        )

        # 初始化重试策略
        self.retry_policy = RetryPolicy(
            max_retries=self.task.retry_policy["max_retries"],
            base_delay=self.task.retry_policy["base_delay"],
        )

        logger.info(
            f"Task loaded: {self.task.task_name} "
            f"({len(self.task.checkpoints)} checkpoints)"
        )

    async def setup_branch(self) -> None:
        """设置工作分支"""
        if not self.task:
            raise RuntimeError("Task not loaded")

        logger.info(f"Setting up branch: {self.task.output_branch}")

        # 检查分支是否存在
        result = await self.run_command(
            f"git rev-parse --verify {self.task.output_branch}",
            check=False,
        )

        if result.returncode == 0:
            # 分支存在，切换
            await self.run_command(f"git checkout {self.task.output_branch}")
            logger.info(f"Switched to existing branch: {self.task.output_branch}")
        else:
            # 创建新分支
            await self.run_command(f"git checkout -b {self.task.output_branch} {self.task.base_branch}")
            logger.info(f"Created new branch: {self.task.output_branch}")

    async def execute_task(self) -> None:
        """执行任务"""
        if not self.task:
            raise RuntimeError("Task not loaded")

        logger.info(f"🜏 Starting task: {self.task.task_name}")
        logger.info(f"Description: {self.task.description}")

        # 设置分支
        await self.setup_branch()

        # 确定起始检查点
        start_checkpoint_index = 0
        if self.recover_from_checkpoint:
            start_checkpoint_index = await self.find_last_successful_checkpoint()
            if start_checkpoint_index > 0:
                logger.info(
                    f"Recovering from checkpoint {start_checkpoint_index + 1}"
                )

        # 执行检查点
        for i, checkpoint in enumerate(self.task.checkpoints[start_checkpoint_index:], start=start_checkpoint_index):
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Checkpoint {i + 1}/{len(self.task.checkpoints)}: {checkpoint.id}")
            logger.info(f"Description: {checkpoint.description}")
            logger.info(f"{'=' * 60}\n")

            try:
                # 执行检查点
                await self.execute_checkpoint(checkpoint)

                # 验证
                await self.validate_checkpoint(checkpoint)

                # 提交
                await self.commit_checkpoint(checkpoint)

                # 记录成功
                await self.record_checkpoint(checkpoint, "success")

                # 发送心跳
                await self.send_heartbeat()

                logger.info(f"✅ Checkpoint {checkpoint.id} completed")

            except Exception as err:
                logger.error(f"❌ Checkpoint {checkpoint.id} failed: {err}")

                # 记录失败
                await self.record_checkpoint(checkpoint, "failed", str(err))

                # 处理失败
                await self.handle_checkpoint_failure(checkpoint, err)

                # 根据失败处理策略决定是否继续
                if self.task.failure_handling.get("on_test_failure") == "rollback_to_last_checkpoint":
                    logger.info("Rolling back to last successful checkpoint")
                    await self.rollback_to_last_checkpoint()
                    raise

        logger.info(f"\n🎉 Task {self.task.task_name} completed successfully!")

    async def execute_checkpoint(self, checkpoint: Checkpoint) -> None:
        """执行检查点"""
        logger.info("Executing checkpoint tasks:")
        for task in checkpoint.tasks:
            logger.info(f"  - {task}")

        # 这里需要实际的代码生成/修改逻辑
        # 在真实实现中，可以调用 Claude API 或其他代码生成工具
        logger.warning(
            "⚠️ Checkpoint execution requires manual implementation or AI assistance"
        )
        logger.info(
            f"Files to modify: {', '.join(checkpoint.files)}"
        )

        # 等待用户确认（实际实现中应该自动化）
        # input("Press Enter when checkpoint tasks are completed...")

    async def validate_checkpoint(self, checkpoint: Checkpoint) -> None:
        """验证检查点"""
        logger.info("Validating checkpoint...")

        command = checkpoint.validation["command"]
        expected = checkpoint.validation["expected"]

        logger.info(f"Running validation: {command}")

        result = await self.run_command(command, check=False)

        if result.returncode != 0:
            logger.error(f"Validation failed with exit code {result.returncode}")
            logger.error(f"Output: {result.stdout}")
            logger.error(f"Error: {result.stderr}")
            raise RuntimeError(f"Validation failed: {expected}")

        logger.info(f"✅ Validation passed: {expected}")

    async def commit_checkpoint(self, checkpoint: Checkpoint) -> None:
        """提交检查点"""
        logger.info("Committing checkpoint...")

        # 添加文件
        for file_path in checkpoint.files:
            await self.run_command(f"git add {file_path}")

        # 提交
        commit_msg = checkpoint.commit_message
        await self.run_command(f'git commit -m "{commit_msg}"')

        # 获取提交 SHA
        result = await self.run_command("git rev-parse HEAD")
        commit_sha = result.stdout.strip()

        logger.info(f"✅ Committed: {commit_sha[:7]} - {commit_msg}")

    async def record_checkpoint(
        self,
        checkpoint: Checkpoint,
        status: str,
        error: str | None = None,
    ) -> None:
        """记录检查点状态"""
        # 获取当前提交
        result = await self.run_command("git rev-parse HEAD", check=False)
        commit_sha = result.stdout.strip() if result.returncode == 0 else None

        record = {
            "checkpoint_id": checkpoint.id,
            "agent_id": self.agent_id,
            "status": status,
            "timestamp": time.time(),
            "error": error,
            "commit_sha": commit_sha,
        }

        checkpoint_file = self.checkpoint_dir / f"{checkpoint.id}.json"
        checkpoint_file.write_text(json.dumps(record, indent=2))

        logger.info(f"Recorded checkpoint: {checkpoint.id} ({status})")

    async def send_heartbeat(self) -> None:
        """发送心跳"""
        heartbeat_file = self.base_dir / f"docs/refactoring/heartbeats/{self.agent_id}.json"
        heartbeat_file.parent.mkdir(parents=True, exist_ok=True)

        heartbeat = {
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "status": "working",
        }

        heartbeat_file.write_text(json.dumps(heartbeat, indent=2))

    async def find_last_successful_checkpoint(self) -> int:
        """查找最后成功的检查点"""
        if not self.task:
            return 0

        for i, checkpoint in enumerate(self.task.checkpoints):
            checkpoint_file = self.checkpoint_dir / f"{checkpoint.id}.json"
            if not checkpoint_file.exists():
                return i

            record = json.loads(checkpoint_file.read_text())
            if record["status"] != "success":
                return i

        return len(self.task.checkpoints)

    async def rollback_to_last_checkpoint(self) -> None:
        """回滚到最后成功的检查点"""
        last_success_index = await self.find_last_successful_checkpoint()

        if last_success_index == 0:
            logger.warning("No successful checkpoint to rollback to")
            return

        last_checkpoint = self.task.checkpoints[last_success_index - 1]
        checkpoint_file = self.checkpoint_dir / f"{last_checkpoint.id}.json"
        record = json.loads(checkpoint_file.read_text())

        commit_sha = record["commit_sha"]
        if commit_sha:
            await self.run_command(f"git reset --hard {commit_sha}")
            logger.info(f"Rolled back to checkpoint {last_checkpoint.id} ({commit_sha[:7]})")

    async def handle_checkpoint_failure(
        self,
        checkpoint: Checkpoint,
        error: Exception,
    ) -> None:
        """处理检查点失败"""
        logger.error(f"Handling checkpoint failure: {error}")

        # 根据失败类型决定处理策略
        if "test" in str(error).lower():
            strategy = self.task.failure_handling.get("on_test_failure", "notify_orchestrator")
        elif "validation" in str(error).lower():
            strategy = self.task.failure_handling.get("on_validation_failure", "notify_orchestrator")
        else:
            strategy = self.task.failure_handling.get("on_fatal_error", "notify_orchestrator")

        logger.info(f"Failure handling strategy: {strategy}")

        if strategy == "notify_orchestrator":
            await self.notify_orchestrator_failure(checkpoint, error)

    async def notify_orchestrator_failure(
        self,
        checkpoint: Checkpoint,
        error: Exception,
    ) -> None:
        """通知主控代理失败"""
        failure_file = self.base_dir / f"docs/refactoring/failures/{self.agent_id}.json"
        failure_file.parent.mkdir(parents=True, exist_ok=True)

        failure = {
            "agent_id": self.agent_id,
            "checkpoint_id": checkpoint.id,
            "error": str(error),
            "timestamp": time.time(),
        }

        failure_file.write_text(json.dumps(failure, indent=2))
        logger.info("Notified orchestrator of failure")

    async def run_command(
        self,
        command: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """运行命令"""
        logger.debug(f"Running: {command}")

        result = subprocess.run(
            command,
            shell=True,
            cwd=self.base_dir,
            capture_output=True,
            text=True,
        )

        if check and result.returncode != 0:
            raise RuntimeError(
                f"Command failed: {command}\n"
                f"Exit code: {result.returncode}\n"
                f"Output: {result.stdout}\n"
                f"Error: {result.stderr}"
            )

        return result

    async def run(self) -> None:
        """运行代理工作器"""
        try:
            await self.load_task()
            await self.execute_task()
            logger.info(f"✅ {self.agent_id} completed successfully")
        except Exception as err:
            logger.exception(f"❌ {self.agent_id} failed: {err}")
            sys.exit(1)


async def main() -> None:
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Lipro-Hass Agent Worker")
    parser.add_argument(
        "--agent-id",
        required=True,
        help="Agent ID (e.g., agent-1)",
    )
    parser.add_argument(
        "--task-file",
        type=Path,
        required=True,
        help="Task definition file",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Base directory (default: current directory)",
    )
    parser.add_argument(
        "--recover-from-checkpoint",
        action="store_true",
        help="Recover from last successful checkpoint",
    )

    args = parser.parse_args()

    worker = AgentWorker(
        agent_id=args.agent_id,
        task_file=args.task_file,
        base_dir=args.base_dir,
        recover_from_checkpoint=args.recover_from_checkpoint,
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
