<template>
  <h1>Preview Model: Ontology-416.owl</h1>
  <div>
    <div style="height:calc(100vh - 160px);">
      <RelationGraph
        ref="graphRef"
        :options="graphOptions"
        :on-node-click="onNodeClick"
        :on-line-click="onLineClick"
      />
    </div>
  </div>
</template>

<script>
import RelationGraph from 'relation-graph/vue3'
export default {
  name: 'Graph',
  components: { RelationGraph },
  data() {
    return {
      graphData: '',
      graphOptions: {
        moveToCenterWhenRefresh: false,
        zoomToFitWhenRefresh: false,
        useAnimationWhenRefresh: true,
        defaultFocusRootNode: false,
        backgrounImageNoRepeat: true,
        defaultExpandHolderPosition: 'top',
        defaultNodeBorderWidth: 5,
        defaultLineWidth: 3,
        defaultLineShape: 5,
        defaultLineMarker: {
          markerWidth: 12,
          markerHeight: 12,
          refX: 6,
          refY: 6,
          data: 'M2,2 L10,6 L2,10 L6,6 L2,2',
        },
        layouts: [
          {
            label: '中心',
            layoutName: 'force',
            maxLayoutTimes: 300,
            force_node_repulsion: 0.9,
            force_line_elastic: 1,
          },
        ],
      },
    }
  },
  mounted() {
    this.showGraph()
  },
  methods: {
    showGraph() {
      this.graphData = {
        rootId: 'a',
        nodes: [
          { id: 'a', text: 'A', borderColor: 'yellow' },
          { id: 'b', text: 'B', color: '#43a2f1', fontColor: 'yellow' },
          { id: 'c', text: 'C', nodeShape: 1, width: 80, height: 60 },
          { id: 'e', text: 'E', nodeShape: 0, width: 150, height: 150 },
        ],
        lines: [
          { from: 'a', to: 'b', text: '关系1', color: '#43a2f1' },
          { from: 'a', to: 'c', text: '关系2' },
          { from: 'a', to: 'e', text: '关系3' },
          { from: 'b', to: 'e', color: '#67C23A' },
        ],
      }
      // 以上数据中的node和link可以参考"Node节点"和"Link关系"中的参数进行配置
      this.$refs.graphRef.setJsonData(this.graphData, graphInstance => {
        // Called when the relation-graph is completed
      })
    },
    onNodeClick(nodeObject, $event) {
      console.log('onNodeClick:', nodeObject)
    },
    onLineClick(lineObject, $event) {
      console.log('onLineClick:', lineObject)
    },
  },
}
</script>
