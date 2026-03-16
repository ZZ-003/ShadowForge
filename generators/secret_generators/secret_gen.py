from NetworkStr_Gen import NetworkGen , Strtype
from Key_Gen import APIkeygen , Platform
import secrets

def Keygen(modeset:int) -> str:
    index=(modeset%(len(Platform)-1))+1
    return APIkeygen(index)

def Strgen(modeset:int) -> str:
    index=(modeset%(len(Strtype)-1))+1
    return NetworkGen(index)

def RandKeygen() -> str:
    modeset:int=secrets.randbelow(65536)
    return Keygen(modeset)

def RandStrgen() -> str:
    modeset:int=secrets.randbelow(65536)
    return Strgen(modeset)

def AllRandgen() -> str:
    modesetA=secrets.randbelow(65536)&0b01
    match modesetA:
        case 0:
            return RandKeygen()
        case 1:
            return RandStrgen()
        case default:
            raise ValueError('Unexpected Modeset Insertion')
        