<template>
  <el-form :inline="true" :model="formInline">
    <el-form-item label="Domain">
      <el-input v-model="formInline.domain" placeholder="Domain" clearable />
    </el-form-item>
    <el-form-item label="Relationship">
      <el-select
        v-model="formInline.relationship"
        placeholder="Relationship"
        clearable
      >
        <el-option label="Zone one" value="shanghai" />
        <el-option label="Zone two" value="beijing" />
      </el-select>
    </el-form-item>
    <el-form-item label="Target">
      <el-input v-model="formInline.target" placeholder="Target" clearable />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onSubmit">Query</el-button>
    </el-form-item>
  </el-form>

  <div>
    查询结果关系图：
    <div style="height:calc(100vh - 450px);">
      <RelationGraph
        ref="graphRef"
        :options="graphOptions"
        :on-node-click="onNodeClick"
        :on-line-click="onLineClick"
      />
    </div>
    查询结果列表：
    <div>
      <el-table :data="tableData" strip style="width: 100%" table-layout="auto">
        <el-table-column prop="index" label="Index" />
        <el-table-column prop="domain" label="Domain" />
        <el-table-column prop="relationship" label="Relationship" />
        <el-table-column prop="target" label="Target" />
      </el-table>
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
      formInline: '',
      graphOptions: {
        backgroundImageNoRepeat: true,
        moveToCenterWhenRefresh: false,
        zoomToFitWhenRefresh: false,
        backgrounImageNoRepeat: true,
        defaultNodeBorderWidth: 5,
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
        rootId: 'part',
        nodes: [
          { id: 'tool', text: '铣刀0.2-40134031' },
          {
            id: 'part',
            text: '副喷口-KJ80341025-1',
            color: '#FF734D',
            borderWidth: 0,
          },
          { id: 'process', text: '工序20' },
          { id: 'feature', text: '大端面' },
          { id: 'machine', text: '数控龙门铣' },
          { id: 'machine', text: '工单-KJ80341025-20-1' },
          { id: 'parameter', text: '工艺参数' },
          { id: 'test', text: '流试记录' },
        ],
        lines: [
          { from: 'tool', to: 'part', text: 'WORK_ON' },
          { from: 'part', to: 'process', text: 'HAS_PROCESS' },
          { from: 'part', to: 'feature', text: 'HAS_FEATURE' },
          { from: 'part', to: 'machine', text: 'USE_MACHINE' },
          { from: 'part', to: 'parameter', text: 'USE_PARAMETER' },
          { from: 'part', to: 'test', text: 'HAS_TEST' },
        ],
      },
      tableData: [
        {
          index: 1,
          domain: '铣刀0.2-40134031',
          relationship: 'WORK_ON',
          target: '副喷口-KJ80341025-1',
        },
        {
          index: 2,
          domain: '副喷口-KJ80341025-1',
          relationship: 'HAS_PROCESS',
          target: '工序20',
        },
        {
          index: 3,
          domain: '副喷口-KJ80341025-1',
          relationship: 'USE_MACHINE',
          target: '大端面',
        },
        {
          index: 4,
          domain: '副喷口-KJ80341025-1',
          relationship: 'HAS_PROCESS',
          target: '数控龙门铣',
        },
        {
          index: 5,
          domain: '副喷口-KJ80341025-1',
          relationship: 'USE_PARAMETER',
          target: '工艺参数',
        },
        {
          index: 6,
          domain: '副喷口-KJ80341025-1',
          relationship: 'HAS_TEST',
          target: '流试记录',
        },
      ],
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
