from typing import Callable, Type, Optional
from inspect import signature, Parameter

from fastapi import Request, APIRouter, Header, HTTPException
from fastapi.responses import Response

import httpx

from api_gateway.models.path_info import PathInfo
from api_gateway.models.response import AccessToken
from api_gateway.settings import settings


def add_param(func: Callable, name: str, annotation: Type,
              kind=Parameter.POSITIONAL_OR_KEYWORD, default=...):
    param = Parameter(name=name, kind=kind, annotation=annotation,
                      default=default)
    sig = signature(func)
    params = tuple(sig.parameters.values())
    if kind == Parameter.POSITIONAL_ONLY:
        params = (param, *params)
    else:
        params = (*params, param)
    func.__signature__ = sig.replace(parameters=params)


def delete_kwargs(func: Callable):
    sig = signature(func)
    params = tuple([
        v for k, v in sig.parameters.items() if k != 'kwargs'
    ])
    func.__signature__ = sig.replace(parameters=params)


async def get_token_by_value(token: str) -> Optional[AccessToken]:
    url = f'http://{settings.AUTH.HOST}:{settings.AUTH.PORT}'
    async with httpx.AsyncClient(base_url=url) as client:
        response = await client.put(f'/tokens/', json={'value': token})
    if not response.is_error:
        return AccessToken(**response.json())


def generate_handler(name: str, path_info: PathInfo, router: APIRouter) \
        -> Callable:
    async def handler(request: Request, **kwargs):
        token = None
        if path_info.authorized:
            raw_token = kwargs.get('x_auth_token', '')
            if not (token := await get_token_by_value(raw_token)):
                raise HTTPException(status_code=401)

        host, port = path_info.service.HOST, path_info.service.PORT
        service_path = path_info.service_path.format(**request.path_params)
        url = f'http://{host}:{port}{service_path}'
        headers = [(k, v) for k, v in request.headers.items()]
        if token:
            headers.append(('x-user-id', str(token.user_id)))

        async with httpx.AsyncClient() as client:
            response = await client.request(
                url=url,
                method=path_info.method,
                params=request.query_params,
                content=await request.body(),
                headers=headers
            )
        return Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers
        )

    delete_kwargs(handler)

    if path_info.request_model:
        add_param(handler, 'payload', path_info.request_model,
                  Parameter.POSITIONAL_ONLY)

    for param, annotation in path_info.path_params.items():
        add_param(handler, param, annotation)

    if path_info.authorized:
        add_param(handler, 'x_auth_token', Optional[str], default=Header(None))

    handler.__name__ = name

    deco = getattr(router, path_info.method.lower())
    return deco(
        path_info.path,
        status_code=path_info.status_code,
        response_model=path_info.response_model,
        responses=path_info.responses
    )(handler)
