package com.xmy.config;

import java.util.HashMap;
import java.util.Map;

public class GraphConfig {
    public static Map<String, String> nodeColor = new HashMap<>() {{
        put("术语", "#409EFF");
        put("实体类", "#67C23A");
        put("活动类", "#E6A23C");
    }};
    public static Map<String, Integer> nodeShape = new HashMap<>() {{
        put("术语", 1);
        put("实体类", 0);
        put("活动类", 0);
    }};

}
