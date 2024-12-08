import request from '@/utils/request'

export const List = data => {
  return request({
    url: '/api/graph/list',
    method: 'get',
  })
}

export const GetNodeProperty = params => {
  return request({
    url: '/api/graph/GetNodeProperty',
    method: 'get',
    params,
  })
}
