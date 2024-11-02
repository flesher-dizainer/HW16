from abc import ABC, abstractmethod
from typing import Any
from archive_extractor import ArchiveManager  # Импорт модуля распаковки
from openai import OpenAI

class AIStrategy(ABC):
    @abstractmethod
    def process_request(self, prompt: str, data: str) -> str:
        raise NotImplementedError


class ProcessingContext:
    def __init__(self):
        self.state: ProcessingState = None
        self.data: Any = None
        self.results: Any = None

    def process(self, data: Any, ai_strategy: AIStrategy):
        self.state.process(self, data, ai_strategy)


class AIProcessorFacade:
    def __init__(self, ai_strategy: AIStrategy):
        self.ai_strategy = ai_strategy
        self.context = ProcessingContext()

    def process_homework(self, archive_path: str):
        # Явно задаем последовательность состояний
        self.context.state = UnpackState(target_dir="temp")
        self.context.process(archive_path, self.ai_strategy)

        self.context.state = AICheckState(prompt="Check this homework", temperature=0.7)
        self.context.process(self.context.data, self.ai_strategy)

        self.context.state = ReportState(format="markdown")
        self.context.process(self.context.results, self.ai_strategy)

    def process_comments(self, comment: str):
        self.context.state = AICheckState(prompt="Check this comment", temperature=0.5)
        self.context.process(comment, self.ai_strategy)

        self.context.state = ResponseState(format="text")
        self.context.process(self.context.results, self.ai_strategy)


class ProcessingState(ABC):
    @abstractmethod
    def process(self, context: 'ProcessingContext', data: Any, ai_strategy: AIStrategy) -> None:
        pass


class UnpackState(ProcessingState):
    def __init__(self, target_dir: str):
        self.target_dir = target_dir

    def process(self, context: ProcessingContext, data: str, ai_strategy: AIStrategy):
        # Распаковка архива
        archive = ArchiveManager()
        archive.extract(data)
        context.data = f"Unpacked data from {data}"


class AICheckState(ProcessingState):
    def __init__(self, prompt: str, temperature: float):
        self.prompt = prompt
        self.temperature = temperature

    def process(self, context: ProcessingContext, data: Any, ai_strategy: AIStrategy):
        result = ai_strategy.process_request(self.prompt, data)
        context.results = result


class ReportState(ProcessingState):
    def __init__(self, format: str):
        self.format = format

    def process(self, context: ProcessingContext, data: Any, ai_strategy: AIStrategy):
        print(f"Generated {self.format} report with {data}")


class ResponseState(ProcessingState):
    def __init__(self, format: str):
        self.format = format

    def process(self, context: ProcessingContext, data: Any, ai_strategy: AIStrategy):
        print(f"Generated {self.format} response with {data}")


class OpenAIStrategy(AIStrategy):
    def __init__(self, api_key: str, base_url: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def process_request(self, prompt: str, data: str) -> str:
        return f"AI processed: {data}"




# Пример использования:
if __name__ == "__main__":
    arch = ArchiveManager()
    arch.extract(r"D:\arch_test_dir.zip", r"D:\\")

    # Использование
    ai_strategy = OpenAIStrategy(api_key="key", base_url="url")
    processor = AIProcessorFacade(ai_strategy)

    # Проверка ДЗ - последовательно выполнит Unpack -> AICheck -> Report
    processor.process_homework("homework.zip")

    # Проверка комментария - выполнит AICheck -> Response
    processor.process_comments("comment text")
