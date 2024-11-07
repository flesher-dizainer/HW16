from abc import ABC, abstractmethod
import zipfile
import tarfile
import rarfile
import py7zr
import os


class AbstractArchive(ABC):
    """
    Абстрактный класс для архивов.
    """

    @abstractmethod
    def extract(self, path: str, destination: str = None) -> None:
        """
        Извлекает содержимое архива.

        Args:
            path: Путь к архиву.
            destination: Путь к папке, куда извлечь содержимое.
        """
        pass


class ZipArchive(AbstractArchive):
    """
    Класс для ZIP архивов.
    """

    def extract(self, path: str, destination: str = None) -> None:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(destination)


class TarArchive(AbstractArchive):
    """
    Класс для TAR архивов.
    """

    def extract(self, path: str, destination: str = None) -> None:
        with tarfile.open(path, 'r') as tar_ref:
            tar_ref.extractall(destination)


class RarArchive(AbstractArchive):
    """
    Класс для RAR архивов.
    """

    def extract(self, path: str, destination: str = None) -> None:
        with rarfile.RarFile(path, 'r') as rar_ref:
            rar_ref.extractall(destination)


class SevenZipArchive(AbstractArchive):
    """
    Класс для 7z архивов.
    """

    def extract(self, path: str, destination: str = None) -> None:
        with py7zr.SevenZipFile(path, 'r') as sevenzip_ref:
            sevenzip_ref.extractall(destination)


class ArchiveManager:
    """
    Класс для управления архивами.
    """

    archive_classes: dict[str, type[AbstractArchive]] = {
        '.zip': ZipArchive,
        '.tar': TarArchive,
        '.rar': RarArchive,
        '.7z': SevenZipArchive
    }

    def extract(self, archive_path: str, destination: str = None) -> None:
        """

        :param archive_path:
        :param destination:
        :return:

        :raises:
            FileNotFoundError: Если архив не найден
            ValueError: Если формат архива не поддерживается
        """
        archive_path = archive_path.strip('"')  # убираем из пути первые и последние кавычки
        extension = os.path.splitext(archive_path)[1].lower()  # получаем расширение
        if destination is None:
            destination = os.path.splitext(archive_path)[0]
        if extension in self.archive_classes:
            os.makedirs(destination, exist_ok=True)
            archive_class = self.archive_classes[extension]
            archive = archive_class()
            try:
                archive.extract(archive_path, destination)
            except FileNotFoundError:
                raise ValueError('Archive File not found')
        else:
            raise ValueError(f"Неподдерживаемый формат архива: {extension}")
