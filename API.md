## API: list

* 기능: 최근일자의 종목 별 주식가격 리턴

* URI
   - IP:port/api-list

* Client --> Server
  - Format: JSON
     - `top_k`: 리턴받고자 하는 종목 최대 개수
  - Example

```python
{
   "top_k": "10"
}
```

* Server --> Client
  - Format: JSON
  - Example
  
```python
* Success case
{"msg":"삼성전자","result":1000.0}

* Fail case
{"msg":"결과값 생성에 실패하였습니다.", result":null}
{"msg":"top_k 값이 주어져있지 않습니다.", result":null}
```
