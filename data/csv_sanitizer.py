import csv


class CsvSanitizer:
    sniffer = csv.Sniffer()
    

    def clean(self, filename, header):
        with open(filename, 'a+') as file:
            file.seek(0)
            data = file.read()

            is_csv = self.__is_csv(data)
            if not is_csv:
                raise csv.Error('File is not a CSV')

            has_header = self.sniffer.has_header(data)
            if not has_header:
                file.truncate(0)
                file.write(f'{header}\n')
                file.write(data)


    def __is_csv(self, sample) -> bool:
        try:
            self.sniffer.sniff(sample)
            return True
        except csv.Error:
            return False
                    