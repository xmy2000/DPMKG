<template>
  <el-row :gutter="20">
    <el-col :span="10">
      <el-input
        v-model="input"
        :autosize="{ minRows: 4 }"
        type="textarea"
        placeholder="Input SWRL"
      />
    </el-col>

    <el-button type="primary" size="large">Execute</el-button>
  </el-row>
  <br />
  <div>
    <div style="height:calc(100vh - 220px);">
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
  name: 'SWRL',
  components: { RelationGraph },
  data() {
    return {
      input: '',
      graphOptions: {
        backgroundImageNoRepeat: true,
        moveToCenterWhenRefresh: false,
        zoomToFitWhenRefresh: false,
        backgrounImageNoRepeat: true,
        defaultNodeBorderWidth: 0,
        defaultLineWidth: 3,
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
            force_node_repulsion: 1,
            force_line_elastic: 1,
          },
        ],
      },
      graphData: {
        rootId: 'toolList',
        nodes: [
          {
            id: 'tool1',
            text: '整体镗刀-40105330',
            color: '#FF734D',
            height: 100,
            width: 100,
          },
          {
            id: 'toolList',
            text: '刀具清单-KJ80341026-20',
            nodeShape: 1,
            color: '#8574A6',
            height: 50,
            width: 100,
          },
          {
            id: 'work1',
            text: '工单-KJ80341026-20-1',
            nodeShape: 1,
            height: 50,
            width: 100,
          },
          {
            id: 'work2',
            text: '工单-KJ80341026-20-2',
            nodeShape: 1,
            height: 50,
            width: 100,
          },
          {
            id: 'work3',
            text: '工单-KJ80341026-20-3',
            nodeShape: 1,
            height: 50,
            width: 100,
          },
          {
            id: 'part1',
            text: '主喷口-KJ80341026-1',
            color: '#00C89B',
            height: 100,
            width: 100,
          },
          {
            id: 'part2',
            text: '主喷口-KJ80341026-2',
            color: '#00C89B',
            height: 100,
            width: 100,
          },
          {
            id: 'part3',
            text: '主喷口-KJ80341026-3',
            color: '#00C89B',
            height: 100,
            width: 100,
          },
        ],
        lines: [
          { from: 'toolList', to: 'tool1', text: 'INCLUDE' },
          { from: 'work1', to: 'toolList', text: 'DEPEND' },
          { from: 'work2', to: 'toolList', text: 'DEPEND' },
          { from: 'work3', to: 'toolList', text: 'DEPEND' },
          { from: 'work1', to: 'part1', text: 'IS_ABOUT' },
          { from: 'work2', to: 'part2', text: 'IS_ABOUT' },
          { from: 'work3', to: 'part3', text: 'IS_ABOUT' },
          {
            from: 'tool1',
            to: 'part1',
            text: 'WORK_ON',
            color: '#FF0016',
            lineWidth: 3,
          },
          {
            from: 'tool1',
            to: 'part2',
            text: 'WORK_ON',
            color: '#FF0016',
            lineWidth: 3,
          },
          {
            from: 'tool1',
            to: 'part3',
            text: 'WORK_ON',
            color: '#FF0016',
            lineWidth: 3,
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
      this.$refs.graphRef.setJsonData(this.graphData, graphInstance => {
        // Called when the relation-graph is completed
      })
    },
  },
}
</script>
