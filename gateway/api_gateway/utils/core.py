from typing import Callable, Type, Optional
from inspect import signature, Parameter

from fastapi import Request, APIRouter, Header
from fastapi.responses import Response

import httpx

from api_gateway.models.path_info import PathInfo


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


def generate_handler(name: str, path_info: PathInfo, router: APIRouter) \
        -> Callable:
    async def handler(request: Request, **kwargs):
        host, port = path_info.service.HOST, path_info.service.PORT
        service_path = path_info.service_path.format(**request.path_params)
        url = f'http://{host}:{port}{service_path}'
        async with httpx.AsyncClient() as client:
            response = await client.request(
                url=url,
                method=path_info.method,
                params=request.query_params,
                content=await request.body(),
                headers=[(k, v) for k, v in request.headers.items()]
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
