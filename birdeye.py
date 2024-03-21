from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import NamedTuple, TypedDict, Union
from decimal import Decimal
import requests

class Settings(BaseSettings):
    BIRD_EYE_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env")

class NoPositionsError(Exception):
    """
    Exception raised when no positions (tokens) are provided.
    """
    def __init__(self, message="No positions provided."):
        self.message = message
        super().__init__(self.message)

class InvalidToken(Exception):
    """
    Exception raised when the API call to fetch token prices is unsuccessful.
    """
    def __init__(self, message="Failed to fetch token prices."):
        self.message = message
        super().__init__(self.message)

class InvalidSolanaAddress(Exception):
    """
    Exception raised when invalid solana address is passed.
    """
    def __init__(self, message="Invalid solana address."):
        self.message = message
        super().__init__(self.message)

class PriceInfo(NamedTuple):
    price: Decimal
    liquidity: Decimal

class TokenOverview(TypedDict):
    key: Union[float, str]


# ============================================================== #

class BirdEyeClient:

    def __init__(self) -> None:
        self.config = Settings()
        
    @property
    def _headers(self):
        return {
            "accept": "application/json",
            "x-chain": "solana",
            "X-API-KEY": self.config.BIRD_EYE_TOKEN,
        }
    
    def _make_api_call(self, method: str, query_url: str, *args, **kwargs) -> requests.Response:
        if method.lower() not in ['get', 'post']:
            raise ValueError(f'Unrecognised method "{method}" passed for query - {query_url}')
        
        if method.lower() == 'get':
            response = requests.get(query_url, *args, **kwargs)
        elif method.lower() == 'post':
            response = requests.post(query_url, *args, **kwargs)

        return response
    
    def fetch_prices(self, token_addresses: list[str]) -> dict[str, PriceInfo[Decimal, Decimal]]:
        if not token_addresses:
            raise NoPositionsError("No tokens provided")
        
        token_address_csv = ','.join(token_addresses)
        url = f'https://public-api.birdeye.so/public/multi_price?list_address={token_address_csv}'
        multi_price_res = self._make_api_call('get', url, headers=self._headers)
        if multi_price_res.status_code != 200:
            raise InvalidToken(f"Failed to fetch prices for tokens {token_addresses}")
        
        url = 'https://public-api.birdeye.so/public/tokenlist?sort_by=v24hUSD&sort_type=desc'
        tokenlist_res = self._make_api_call('get', url, headers=self._headers)
        if tokenlist_res.status_code != 200:
            raise InvalidToken(f"Failed to fetch prices for tokens {token_addresses}")
        
        # get token value and liquidity
        token_prices = multi_price_res.json()['data']
        token_list = tokenlist_res.json()['data']['tokens']
        
        return {
            token: PriceInfo(Decimal(data['value']), Decimal([t for t in token_list if t['address'] == token][0]['liquidity']))
            for token, data in token_prices.items()
        }



    def fetch_token_overview(self, address: str) -> TokenOverview:
        if not address:
            raise NoPositionsError("No token provided")
        
        url = f'https://public-api.birdeye.so/public/exists_token?address={address}'
        check_token_res = self._make_api_call('get', url, headers=self._headers)
        if check_token_res.status_code != 200:
            raise InvalidToken(f"Failed to fetch token {address}")
        
        if not check_token_res.json()['data']["exists"]:
            raise InvalidSolanaAddress("Invalid solana address")
        
        url = 'https://public-api.birdeye.so/public/tokenlist?sort_by=v24hUSD&sort_type=desc'
        tokenlist_res = self._make_api_call('get', url, headers=self._headers)
        if tokenlist_res.status_code != 200:
            raise InvalidToken(f"Failed to fetch token {address}")
        
        return [t for t in tokenlist_res.json()['data']['tokens'] if t['address'] == address][0]