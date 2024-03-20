from setting import Settings
from pydantic import BaseModel
from typing import Tuple
from decimal import Decimal
import requests

class PriceInfo(BaseModel):
    price: Tuple[Decimal, Decimal]

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
            raise ValueError("No tokens provided")
        
        token_address_csv = ','.join(token_addresses)
        url = f'https://public-api.birdeye.so/public/multi_price?list_address={token_address_csv}'
        response = self._make_api_call('get', url, headers=self._headers)
        
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch prices for tokens {token_addresses}")
        
        '''
        sample response:
        {
            "data": {
                "So11111111111111111111111111111111111111112": {
                "value": 170.31082412623664,
                "updateUnixTime": 1710950218,
                "updateHumanTime": "2024-03-20T15:56:58",
                "priceChange24h": -7.077326862097751
                },
                "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So": {
                "value": 200.01269444682526,
                "updateUnixTime": 1710950218,
                "updateHumanTime": "2024-03-20T15:56:58",
                "priceChange24h": -6.801589095053282
                }
            },
            "success": true
        }
        '''
        return {
            token: PriceInfo(price=(Decimal(data['value']), Decimal(data['priceChange24h'])))
            for token, data in response.json()['data'].items()
        }   



    def fetch_token_overview(self, address: str):
        pass