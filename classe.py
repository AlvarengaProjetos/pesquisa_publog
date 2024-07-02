from ctypes import *

class Publog:

    def __init__(self):
        """
        Construtor da classe Publog que recebe um dicionário contendo as informações de configuração.
        """
        self.MAX_SIZE = 4096
        self.dll_path = 'C:\publog\TOOLS\MS12\DecompDl64.dll'
        self.PATH_TO_FEDLOG = 'C:\publog'
        self.dll = CDLL(self.dll_path)
        self.path = c_char_p(bytes(self.PATH_TO_FEDLOG, encoding='utf-8'))
        self.data = create_string_buffer(self.MAX_SIZE)
        self.error = create_string_buffer(self.MAX_SIZE)
        self.length = c_int(self.MAX_SIZE)  
      
      
    def connect(self):
        """
        Método que realiza a conexão com o IMDConnectDLL.
        """
        if self.dll_path.endswith('DecompDl.dll'):
            self.dll = CDLL(self.dll_path)
        elif self.dll_path.endswith('DecompDl64.dll'):
            self.dll = CDLL(self.dll_path, winmode=0x100)
        else:
            print('Invalid DLL path')
            return False
        if self.dll.IMDConnectDLL(self.path):
            print('Invalid Path\n\n')
            return False
        return True
    
    
    def disconnect(self):
        """
        Método que realiza a desconexão com o IMDConnectDLL.
        """
        self.dll.IMDDisconnectDLL(self.path)
    
    
    def search(self, query):
        """
        Método que realiza a busca por informações no IMD.
        Recebe como parâmetro a query a ser executada.
        Retorna o número de resultados encontrados e os dados em um buffer.
        """
        self.dll.IMDSqlDLL(query.encode('utf-8'), self.data, self.length)
        self.data.value.decode('utf-8')
        return self.data.value.decode('utf-8')
    