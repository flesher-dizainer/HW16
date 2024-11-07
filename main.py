from abc import ABC, abstractmethod
from typing import Any
from archive_extractor import ArchiveManager
from openai import OpenAI
from file_manager import FileManager
from dataclasses import dataclass


@dataclass
class OpenAIConfig:
    """Настройки для взаимодействия с API OpenAI."""

    api_key: str
    """Ключ API OpenAI."""

    base_url: str
    """Базовый URL"""

    model: str = "openai/gpt-4o-mini"
    """Модель OpenAI, используемая по умолчанию."""

    temperature: float = 0.7
    """Температура для генерации текста (от 0 до 1)."""

    max_tokens: int = 3000
    """Максимальное количество токенов для генерации текста."""


class AIStrategy(ABC):
    @abstractmethod
    def process_request(self, prompt: str, data: str, config: OpenAIConfig) -> str:
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

        self.context.state = AICheckState(prompt="Проверь и исправь код", temperature=0.7)
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
        FileManager.delete_directory(self.target_dir)


class AICheckState(ProcessingState):
    def __init__(self, prompt: str, temperature: float) -> None:
        self.prompt = prompt
        self.temperature = temperature

    def process(self, context: ProcessingContext, data: Any, ai_strategy: AIStrategy) -> None:
        ai_strategy.config.temperature = self.temperature
        result = ai_strategy.process_request(self.prompt, data, ai_strategy.config)
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
    def __init__(self, config: OpenAIConfig) -> None:
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)
        self.config = config

    def process_request(self, prompt: str, data: str, config: OpenAIConfig) -> str:
        message = [{
            "role": "user",
            "content": prompt + '\n' + data
        }]
        request = self.client.chat.completions.create(
            messages=message,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            extra_headers={"X-Title": "My App"},
        )
        return request.choices[0].message.content


# Пример использования:
if __name__ == "__main__":
    try:
        ai_config = OpenAIConfig(
            api_key='YOU API KEY',
            base_url='API Open AI URL',
            model='gpt-4o-mini'
        )
        ai_strategy = OpenAIStrategy(ai_config)
        processor = AIProcessorFacade(ai_strategy)

        path_archive = input('Введите путь к архиву: ')
        processor.process_homework(path_archive)

        processor.process_comments("comment text")
    except ValueError as err:
        print(f'Возникла ошибка: {err}')
    except Exception as error:
        print(error)
