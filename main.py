from abc import ABC, abstractmethod
from typing import Any
from archive_extractor import ArchiveManager
from openai import OpenAI
from file_manager import FileManager


class AIStrategy(ABC):
    @abstractmethod
    def process_request(self, prompt: str, data: str) -> str:
        raise NotImplementedError


class ProcessingContext:
    def __init__(self) -> None:
        self.state: ProcessingState = None
        self.data: Any = None
        self.results: Any = None

    def process(self, data: Any, ai_strategy: AIStrategy) -> None:
        self.state.process(self, data, ai_strategy)


class AIProcessorFacade:
    def __init__(self, ai_strategy: AIStrategy) -> None:
        self.ai_strategy = ai_strategy
        self.context = ProcessingContext()

    def process_homework(self, archive_path: str) -> None:
        self.context.state = UnpackState(target_dir="temp")
        self.context.process(archive_path, self.ai_strategy)

        self.context.state = AICheckState(prompt="Check this homework", temperature=0.7)
        self.context.process(self.context.data, self.ai_strategy)

        self.context.state = ReportState(format="markdown")
        self.context.process(self.context.results, self.ai_strategy)

    def process_comments(self, comment: str) -> None:
        self.context.state = AICheckState(prompt="Check this comment", temperature=0.5)
        self.context.process(comment, self.ai_strategy)

        self.context.state = ResponseState(format="text")
        self.context.process(self.context.results, self.ai_strategy)


class ProcessingState(ABC):
    @abstractmethod
    def process(self, context: 'ProcessingContext', data: Any, ai_strategy: AIStrategy) -> None:
        pass


class UnpackState(ProcessingState):
    def __init__(self, target_dir: str) -> None:
        self.target_dir = target_dir

    def process(self, context: ProcessingContext, data: str, ai_strategy: AIStrategy) -> None:
        archive = ArchiveManager()
        archive.extract(data, self.target_dir)
        context.data = FileManager.get_file_data(self.target_dir, '.py')


class AICheckState(ProcessingState):
    def __init__(self, prompt: str, temperature: float) -> None:
        self.prompt = prompt
        self.temperature = temperature

    def process(self, context: ProcessingContext, data: Any, ai_strategy: AIStrategy) -> None:
        ai_strategy.temperature = self.temperature
        result = ai_strategy.process_request(self.prompt, data)
        context.results = result


class ReportState(ProcessingState):
    def __init__(self, format: str) -> None:
        self.format = format

    def process(self, context: ProcessingContext, data: Any, ai_strategy: AIStrategy) -> None:
        print(f"Generated {self.format} report with {data}")


class ResponseState(ProcessingState):
    def __init__(self, format: str) -> None:
        self.format = format

    def process(self, context: ProcessingContext, data: Any, ai_strategy: AIStrategy) -> None:
        print(f"Generated {self.format} response with {data}")


class OpenAIStrategy(AIStrategy):
    def __init__(self, api_key: str, base_url: str) -> None:
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def process_request(self, prompt: str, data: str) -> str:
        message = [{
            "role": "user",
            "content": prompt + '\n' + data
        }]
        request = self.client.chat.completions.create(
            messages=message,
            model='openai/gpt-4o-mini',
            temperature=self.temperature,
            max_tokens=4000,
            extra_headers={"X-Title": "My App"},
        )
        return request.choices[0].message.content


# Пример использования:
if __name__ == "__main__":
    try:
        ai_strategy = OpenAIStrategy(
            api_key="YOUR_API_KEY",
            base_url="https://api.vsegpt.ru/v1")
        processor = AIProcessorFacade(ai_strategy)

        path_archive = input('Введите путь к архиву: ')
        processor.process_homework(path_archive)

        processor.process_comments("comment text")
    except ValueError as err:
        print(f'Возникла ошибка: {err}')
