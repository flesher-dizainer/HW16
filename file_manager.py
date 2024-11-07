import os
import shutil

from chardet import detect


class FileManager:
    @staticmethod
    def get_file_data(dir_files: str, file_extension: str) -> str:
        """
        Возвращает содержимое всех файлов с указанным расширением.

        Args:
            dir_files: путь к файлам.
            file_extension: расширение файла.

        Returns:
            Содержимое всех файлов с расширением file_extension.

        Raises:
            ValueError: Если нет данных из файлов с указанным расширением.
        """
        if not os.path.isdir(dir_files):
            raise FileNotFoundError(f"Директория '{dir_files}' не найдена.")
        file_data = ''
        for root, _, files in os.walk(dir_files):
            for file_name in files:
                if os.path.splitext(file_name)[1].lower() == file_extension.lower():
                    path_file_name = os.path.join(root, file_name)
                    if os.path.exists(path_file_name):
                        with open(path_file_name, 'rb') as f:
                            data = f.read()
                            encoding = detect(data)['encoding']
                        if encoding:
                            with open(path_file_name, 'r', encoding=encoding) as file:
                                file_data += f'File {file_name}\n{file.read()}\n'
                        else:
                            raise ValueError(f'File encoding error: {path_file_name}')
                    else:
                        raise ValueError(f'File not found {path_file_name}')
        if not file_data:
            raise ValueError('Нет данных из файлов с расширением ' + file_extension)
        return file_data
    @staticmethod
    def delete_directory(directory_path):
        """
        Deletes a directory and all its contents.

        Args:
            directory_path (str): The path to the directory to delete.
        """
        try:
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            os.rmdir(directory_path)
            print(f"Directory '{directory_path}' deleted.")
        except FileNotFoundError:
            print(f"Directory '{directory_path}' not found.")
        except OSError as e:
            print(f"Error deleting directory '{directory_path}': {e}")
