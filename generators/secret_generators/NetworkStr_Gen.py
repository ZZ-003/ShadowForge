import secrets 
from enum import Enum
import string

class Strtype(Enum):
    PostgreSQL=1
    MySQL=2
    MongoDB=3
    HTTPAuth=4
    Redis=5
    Sentry=6

class NetworkStr_Gen:
    def __init__(self):
        pass
    
    def ipv4addr_Gen(self) -> str :
        return '.'.join(str(secrets.randbelow(256)) for _ in range(4))
    def portGen(self) -> str:
        port:int=secrets.randbelow(100000)
        return ':'+str(port)
    def id_Gen(self) -> str:
        return str(secrets.randbelow(65536))
    
    def PostgreSQL_Gen(self) -> str :
        baseprefix:str = "postgresql://"
        cstr:str=baseprefix+'testuser'+self.id_Gen()+':'+'TestPass'+self.id_Gen()+'@'+self.ipv4addr_Gen()+self.portGen()+'/testdb'
        return cstr

    def MySQL_Gen(self) -> str :
        baseprefix:str='jdbc:mysql://'
        ipv4:str=self.ipv4addr_Gen()+self.portGen()
        postfix:str='/testdb?user=testuser'+self.id_Gen()+'&password=TestPass'+self.id_Gen()+'!'
        return baseprefix+ipv4+postfix

    def Mongo_Gen(self) -> str:
        baseprefix='mongodb://'
        baseend='/?authSource=admin'
        cstr=baseprefix+'testuser'+self.id_Gen()+':TestPass'+self.id_Gen()+'!@'+self.ipv4addr_Gen()+self.portGen()+baseend
        return cstr

    def HTTPAuth_Gen(self) -> str:
        baseprefix:str='http://'
        addr=self.ipv4addr_Gen()+':8080'
        cstr=baseprefix+'testuser'+self.id_Gen()+':TestPass'+self.id_Gen()+'!@'+addr
        return cstr

    def Redis_Gen(self) -> str:
        baseprefix:str='redis://:TestPass'
        cstr=baseprefix+self.id_Gen()+'!@'+self.ipv4addr_Gen()+self.portGen()+'/0'
        return cstr

    def Sentry_Gen(self) -> str:
        baseprefix:str='http://'
        tokenA:str=secrets.token_hex(16)
        org_id:str=''.join(secrets.choice(string.digits) for _ in range(16))
        basemid:str='.ingest.us.sentry.io/'
        proj_id:str=''.join(secrets.choice(string.digits) for _ in range(16))
        cstr=baseprefix+tokenA+'@o'+org_id+basemid+proj_id
        return cstr

def NetworkGen(modeset:int) -> str:
    Generator=NetworkStr_Gen()
    match Strtype(modeset):
        case Strtype.PostgreSQL:
            return Generator.PostgreSQL_Gen()
        case Strtype.MySQL:
            return Generator.MySQL_Gen()
        case Strtype.MongoDB:
            return Generator.Mongo_Gen()
        case Strtype.HTTPAuth:
            return Generator.HTTPAuth_Gen()
        case Strtype.Redis:
            return Generator.Redis_Gen()
        case Strtype.Sentry:
            return Generator.Sentry_Gen()
        case _:
            raise ValueError('Invalid String Type Index')
        