import os


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
        file_data = ''
        for root, _, files in os.walk(dir_files):
            for file_name in files:
                if os.path.splitext(file_name)[1] == file_extension:
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_data += f'File {file_name}\n{file.read()}\n'

        if not file_data:
            raise ValueError('Нет данных из файлов с расширением ' + file_extension)

        return file_data
