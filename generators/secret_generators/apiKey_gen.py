import secrets
import string
from enum import Enum

class Platform(Enum):
    OpenAI_Personal = 1
    Deepseek        = 2
    BaiLian         = 3     #Aliyun
    OpenAI_Project  = 4     #To do
    Moonshot        = 5
    HuggingFace     = 6
    #To be extended

class KeyRandGen:
    
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
        pass
    
    def HuggingFace_keygen(self) -> str:
        randset=string.ascii_letters
        payload:str=''.join(secrets.choice(randset) for _ in range(34))
        return 'hf_'+payload

def keygen(modeset:int) -> str:
    Generator=KeyRandGen()
    match Platform(modeset):
        case Platform.OpenAI_Personal:
            return Generator.OpenAI_Personal_keygen()
        case Platform.Deepseek:
            return Generator.Deepseek.keygen()
        case Platform.BaiLian:
            return Generator.Balian_keygen()
        case Platform.Moonshot:
            return Generator.Moonshot_keygen()
        case Platform.OpenAI_Project:
            pass
        case Platform.HuggingFace:
            return Generator.HuggingFace_keygen()
        
# Test Only
if __name__ == "__main__":
    print("mode: ",end='')
    mode=int(input())
    print(keygen(mode))