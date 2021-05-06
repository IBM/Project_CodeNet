package com.ibm.ai4code.parser.commons;

import java.io.File;
import java.util.ArrayList;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Queue;
import javax.json.JsonReader;
import javax.json.JsonValue;
import javax.json.JsonWriter;
import javax.json.JsonWriterFactory;
import javax.json.stream.JsonGenerator;
import javax.json.Json;
import javax.json.JsonArray;
import javax.json.JsonArrayBuilder;
import javax.json.JsonNumber;
import javax.json.JsonObject;
import javax.json.JsonObjectBuilder;

public class JsonUtils {
	public static void readJson(String fileName) throws FileNotFoundException {
		File jsonInputFile = new File(fileName);
		InputStream is;
		is = new FileInputStream(jsonInputFile);
		JsonReader reader = Json.createReader(is);
		JsonObject empObj = reader.readObject();
		reader.close();
		JsonObject graphObj = empObj.getJsonObject("graph");
		System.out.println(graphObj.get("version"));
		JsonArray nodes = graphObj.getJsonArray("nodes");
		//System.out.println(nodes);
		for(JsonValue jv: nodes) {
			//System.err.println(jv.getValueType());
			JsonObject jo = (JsonObject) jv;
			//System.out.println(jo);
			System.out.println(jo.getInt("id"));
			System.out.println(jo.getString("label"));
		}
		JsonArray edges = graphObj.getJsonArray("edges");
		for(JsonValue jv: edges) {
			//System.err.println(jv.getValueType());
			JsonObject jo = (JsonObject) jv;
			JsonArray jarr = jo.getJsonArray("between");
			for(JsonValue jarrV: jarr) {
				//System.err.println(jarrV.getValueType());
				JsonNumber _jo = (JsonNumber) jarrV;
				System.out.print(_jo+" ");
			}
			System.out.println();
		}
		
	}
	public static void writeJson(String fileName) throws IOException {
		// step 1 build graph object
		JsonObjectBuilder jGraphBuilder = Json.createObjectBuilder();
		jGraphBuilder.add("version", "1.0");
		jGraphBuilder.add("type", "tree");
		jGraphBuilder.add("directed", true);
		jGraphBuilder.add("root", 0);
		
		//step 2 build nodes array
		
		JsonArrayBuilder nodesArrBuilder = Json.createArrayBuilder();
		nodesArrBuilder.add(Json.createObjectBuilder().add("id", 0).add("label", "Top"));
		nodesArrBuilder.add(Json.createObjectBuilder().add("id", 1).add("label", "Child1"));
		nodesArrBuilder.add(Json.createObjectBuilder().add("id", 2).add("label", "Child2"));
		nodesArrBuilder.add(Json.createObjectBuilder().add("id", 3).add("label", "Grandchild"));
		jGraphBuilder.add("nodes", nodesArrBuilder);
		
		// step 3 builds edges array
		JsonArrayBuilder edgesArrBuilder = Json.createArrayBuilder();
		edgesArrBuilder.add(Json.createObjectBuilder().add("between", Json.createArrayBuilder().add(0).add(1)));
		edgesArrBuilder.add(Json.createObjectBuilder().add("between", Json.createArrayBuilder().add(0).add(2)));
		edgesArrBuilder.add(Json.createObjectBuilder().add("between", Json.createArrayBuilder().add(2).add(3)));
		jGraphBuilder.add("edges", edgesArrBuilder);
		
		
		// step 4 build top object
		JsonObjectBuilder jTopBuilder = Json.createObjectBuilder();
		jTopBuilder.add("graph", jGraphBuilder);
		
		// step 5 write to disk
		Map<String, Object> properties = new HashMap<>(1);
        properties.put(JsonGenerator.PRETTY_PRINTING, true);
        JsonWriterFactory writerFactory = Json.createWriterFactory(properties);
        JsonWriter writer = writerFactory.createWriter(new FileWriter(new File(fileName)));
		writer.writeObject(jTopBuilder.build());
		writer.close();
		
	}
	
	public static void serializeSPT(SPT tree, String fileName) throws IOException {
		// step 1 build graph object
		JsonObjectBuilder jGraphBuilder = Json.createObjectBuilder();
		jGraphBuilder.add("version", "1.0");
		jGraphBuilder.add("src-file", tree.getSrcFileName()); // weiz 2021-03-06
		jGraphBuilder.add("type", "tree");
		jGraphBuilder.add("directed", true);
		jGraphBuilder.add("order", "bfs");
		jGraphBuilder.add("num-of-nodes", tree.getNumNodes());
		jGraphBuilder.add("num-of-edges", tree.getNumEdges());
		jGraphBuilder.add("root", tree.getRoot().getBFSIdx()); // weiz 2021-01-19 revert back to the idea that uses
		                      // traversal id (BFS) as the ID, thus id of the root should always be 0
		
		// jGraphBuilder.add("root", tree.getRoot().getTokenIdx()); // weiz 2020-11-18 , use the token index as "id"
		
		// step 1.5 get the layerwise traversal queue
		Queue<SPTNode> queue = tree.getLayerWiseTraversalQueue();
		assert(queue.size() == tree.getNumNodes());
		// step 2  build nodes array
		JsonArrayBuilder nodesArrBuilder = Json.createArrayBuilder();
		for(SPTNode n: queue) {
			//nodesArrBuilder.add(Json.createObjectBuilder().add("id", n.getIdx()).add("label", n.toString()));// TODO maybe implement getLabel instead of toString
			
			if(n.getType().equals("Token")) {
				nodesArrBuilder.add(Json.createObjectBuilder().add("id", n.getBFSIdx()).add("label", n.getLabel()).
				add("node-type", n.getType()).add("type-rule-name", n.getRuleName()) 
				.add("type-rule-index", n.getRuleIndex()).add("reserved-word-flag", n.getReservedWordFlag())   
		        .add("dfs-index", n.getDFSIndex()).add("depth", n.getDepth()) // weiz 2021-03-05, add more fields
		        .add("token-id", n.getTokenIdx()));// weiz 2020-11-18, use token index as "id"
			}else {
				nodesArrBuilder.add(Json.createObjectBuilder().add("id", n.getBFSIdx()).add("label", n.getLabel()).
				add("node-type", n.getType()).add("type-rule-name", n.getRuleName()) // weiz 2021-01-19, for non-leaf nodes, we don't output token_id
				.add("type-rule-index", n.getRuleIndex()).add("reserved-word-flag", n.getReservedWordFlag())   
		        .add("dfs-index", n.getDFSIndex()).add("depth", n.getDepth())); // weiz 2021-03-05, add more fields
			}
			/* nodesArrBuilder.add(Json.createObjectBuilder().add("id", n.getTokenIdx()).add("label", n.getLabel()).
					add("node-type", n.getType()).add("type-rule-name", n.getRuleName()).add("traversal_id", n.getIdx())); // weiz 2020-11-18, use token index as "id" 
			*/
		}
		jGraphBuilder.add("nodes", nodesArrBuilder);
		
		// step 3 builds edges array
		int edgeNum =0;
		JsonArrayBuilder edgesArrBuilder = Json.createArrayBuilder();
		for(SPTNode n: queue) {
			ArrayList<SPTNode> children = n.getChildren();
			if(children	!=	null) {
				int source = n.getBFSIdx(); // weiz 2021-01-19 revert it back to use BFS id
				//int source = n.getTokenIdx(); // weiz 2020-11-18 use token index as index
				for(SPTNode c: children) {
					int dst = c.getBFSIdx(); // weiz 2020-01-19 revert it back to use BFS id
					//int dst = c.getTokenIdx(); // weiz 2020-11-18 use token index as index
					edgesArrBuilder.add(Json.createObjectBuilder().add("between", Json.createArrayBuilder().add(source).add(dst)));
					edgeNum++;
				}
			}
			
		}
		assert(tree.getNumEdges() == edgeNum);
		
		jGraphBuilder.add("edges", edgesArrBuilder);
		
		// step 4 build top object
		JsonObjectBuilder jTopBuilder = Json.createObjectBuilder();
		jTopBuilder.add("graph", jGraphBuilder);
		
		// step 5 write to disk
		Map<String, Object> properties = new HashMap<>(1);
		properties.put(JsonGenerator.PRETTY_PRINTING, true);
		JsonWriterFactory writerFactory = Json.createWriterFactory(properties);
		//JsonWriter writer = writerFactory.createWriter(new FileWriter(new File(fileName)));
		FileWriter rawFileWriter = new FileWriter(new File(fileName));
		JsonWriter writer = writerFactory.createWriter(rawFileWriter);
		writer.writeObject(jTopBuilder.build());
		rawFileWriter.write(System.lineSeparator());
		writer.close();
		
		
	}
	
	public static void main(String [] args) throws IOException {
		//String fileName = "/Users/weiz/eclipse-workspace/ai4code/resources/tree.json";
		//readJson(fileName);
		String fileName = "/Users/weiz/eclipse-workspace/ai4code/resources/tree_weiz.json";
		writeJson(fileName);
		
	}

}
