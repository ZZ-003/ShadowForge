import secrets
import string
from enum import Enum

class Platform(Enum):
    OpenAI_Personal = 1
    Deepseek        = 2
    Bailian         = 3     #Aliyun
    OpenAI_Project  = 4     #To do
    Moonshot        = 5
    HuggingFace     = 6
    AWSAccess       = 7
    Github          = 8
    OpenSSH         = 9
    #To be extended

class APIKeyRandGen:
    
    def Deepseek_keygen(self) -> str :
        return 'sk-'+secrets.token_hex(16)

    def Bailian_keygen(self) -> str:
        return 'sk-'+secrets.token_hex(16)

    def OpenAI_Personal_keygen(self) -> str:
        randset = string.ascii_letters + string.digits
        payload:str=''.join(secrets.choice(randset) for _ in range(48))
        return 'sk-'+payload

    def Moonshot_keygen(self) -> str:
        randset = string.ascii_letters + string.digits
        payload:str=''.join(secrets.choice(randset) for _ in range(48))
        return 'sk-'+payload

    def OpenAI_Project_keygen(self) -> str:
        return ''
    
    def HuggingFace_keygen(self) -> str:
        randset=string.ascii_letters
        payload:str=''.join(secrets.choice(randset) for _ in range(34))
        return 'hf_'+payload

    def AWSAccess_keygen(self) -> str:
        randset0=string.ascii_uppercase+ string.digits
        randpreset=['AKIA','ASIA','ABIA','ACCA','AGPA']
        randkeyset=string.ascii_letters+string.digits+'/+='
        prefix1=secrets.choice(randpreset)
        prefix2=''.join(secrets.choice(randset0) for _ in range(16))
        keystr:str=prefix1+prefix2+''.join(secrets.choice(randkeyset) for _ in range(40))
        return keystr
    
    def Github_keygen(self) -> str:
        prefix:str='ghp+'
        randset=string.ascii_letters+string.digits
        payload:str=''.join(secrets.choice(randset) for _ in range(36))
        keystr:str=prefix+payload
        return keystr
    
    def OpenSSH_keygen(self) -> str:
        prefix:str='-----BEGIN OPENSSH PRIVATE KEY-----\n'
        end='\n-----END OPENSSH PRIVATE KEY-----\n'
        keystr=''
        return keystr
        





def APIkeygen(modeset:int) -> str:
    Generator=APIKeyRandGen()
    match Platform(modeset):
        case Platform.OpenAI_Personal:
            return Generator.OpenAI_Personal_keygen()
        case Platform.Deepseek:
            return Generator.Deepseek_keygen()
        case Platform.Bailian:
            return Generator.Bailian_keygen()
        case Platform.Moonshot:
            return Generator.Moonshot_keygen()
        case Platform.OpenAI_Project:
            return Generator.OpenAI_Project_keygen()
        case Platform.HuggingFace:
            return Generator.HuggingFace_keygen()
        case Platform.AWSAccess:
            return Generator.AWSAccess_keygen()
        case Platform.Github:
            return Generator.Github_keygen()
        case default:
            raise ValueError('Invalid Platform Index')
        