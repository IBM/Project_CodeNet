package com.ibm.wala.codeNet;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.Iterator;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import com.ibm.wala.util.collections.HashMapFactory;
import com.ibm.wala.util.collections.NonNullSingletonIterator;
import com.ibm.wala.util.graph.Graph;
import com.ibm.wala.util.graph.traverse.DFS;

public class DFSOrderGenerator {

	public static void main(String... args) throws JSONException, FileNotFoundException {
		JSONObject parseTreeJson = 
			(JSONObject)new JSONTokener(new FileInputStream(System.getProperty("parseTreeFile")))
			.nextValue();

		Graph<JSONObject> parseTree = new WalaSPTGraph(parseTreeJson);
		
		Map<JSONObject,Integer> dfs = HashMapFactory.make();
		
		JSONArray nodes = parseTreeJson
			.getJSONObject("graph")
			.getJSONArray("nodes");

		int dfsNumber = 0;
		Iterator<JSONObject> search = DFS.iterateFinishTime(parseTree, new NonNullSingletonIterator<JSONObject>(nodes.getJSONObject(0)));
		while (search.hasNext()) {
			dfs.put(search.next(), dfsNumber++);
		} 
		
		nodes.forEach(n -> {
			JSONObject node = (JSONObject) n;
			System.out.println(node.getInt("id") + " " + dfs.get(node));
		});
		
	}
}
