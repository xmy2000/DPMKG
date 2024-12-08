const Layout = () => import('@/layout/index.vue')
const Model = () => import('@/views/data/model.vue')
const Graph = () => import('@/views/data/graph.vue')
const Preview = () => import('@/views/data/preview.vue')
const SWRL = () => import('@/views/data/swrl.vue')
const Search = () => import('@/views/data/search.vue')

export default [
  {
    path: '/data',
    component: Layout,
    name: 'data',
    meta: {
      title: 'Data Management',
    },
    icon: 'Cpu',
    children: [
      {
        path: 'model',
        name: 'Model List',
        component: Model,
        meta: {
          title: 'Model List',
        },
      },
      {
        path: 'graph',
        name: 'Graph',
        component: Graph,
        meta: {
          title: 'Graph',
        },
      },
      {
        path: 'preview',
        name: 'Preview',
        component: Preview,
        meta: {
          title: 'Preview',
        },
        hidden: true,
      },
      {
        path: 'swrl',
        name: 'SWRL',
        component: SWRL,
        meta: {
          title: 'SWRL',
        },
      },
      {
        path: 'search',
        name: 'Search',
        component: Search,
        meta: {
          title: 'Search',
        },
      },
    ],
  },
]
