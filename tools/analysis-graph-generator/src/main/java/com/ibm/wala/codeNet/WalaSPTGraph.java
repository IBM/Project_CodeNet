package com.ibm.wala.codeNet;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.util.stream.Stream;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import com.ibm.wala.util.collections.EmptyIterator;
import com.ibm.wala.util.collections.HashMapFactory;
import com.ibm.wala.util.collections.HashSetFactory;
import com.ibm.wala.util.graph.AbstractNumberedGraph;
import com.ibm.wala.util.graph.NumberedEdgeManager;
import com.ibm.wala.util.graph.NumberedNodeManager;
import com.ibm.wala.util.intset.IntSet;
import com.ibm.wala.util.intset.IntSetUtil;
import com.ibm.wala.util.intset.MutableIntSet;

public class WalaSPTGraph extends AbstractNumberedGraph<JSONObject> {
	NumberedNodeManager<JSONObject> nodes;
	private NumberedEdgeManager<JSONObject> edges;
	public final int root;
	
	public WalaSPTGraph(String parseTreeFile) throws JSONException, FileNotFoundException {
		this((JSONObject)new JSONTokener(new FileInputStream(parseTreeFile)).nextValue());
	}
	
	public WalaSPTGraph(JSONObject parseTreeJson) {
		root = parseTreeJson
				.getJSONObject("graph")
				.getInt("root");
		
		nodes = new NumberedNodeManager<JSONObject>() {
			private Map<Integer,JSONObject> a = HashMapFactory.make();
			
			{
				parseTreeJson
					.getJSONObject("graph")
					.getJSONArray("nodes")
					.forEach(n -> a.put(((JSONObject)n).getInt("id"), (JSONObject)n));
			}

			@Override
			public Stream<JSONObject> stream() {
				return a.values().stream();
			}

			@Override
			public int getNumberOfNodes() {
				return a.size();
			}

			@Override
			public void addNode(JSONObject n) {
				throw new UnsupportedOperationException();
			}

			@Override
			public void removeNode(JSONObject n) throws UnsupportedOperationException {
				throw new UnsupportedOperationException();
			}

			@Override
			public boolean containsNode(JSONObject n) {
				return a.values().contains(n);
			}

			@Override
			public int getNumber(JSONObject N) {
				return N.getInt("id");
			}

			@Override
			public JSONObject getNode(int number) {
				return a.get(number);
			}

			@Override
			public int getMaxNumber() {
				return a.size();
			}

			@Override
			public Iterator<JSONObject> iterateNodes(IntSet s) {
				Set<JSONObject> result = HashSetFactory.make();
				s.foreach(n -> result.add(getNode(n)));
				return result.iterator();
			}
			
		};
		edges = new NumberedEdgeManager<JSONObject>() {
			private Map<JSONObject,Set<JSONObject>> forward = HashMapFactory.make();
			private Map<JSONObject,Set<JSONObject>> backward = HashMapFactory.make();
			
			{
				Map<Integer,JSONObject> idToNode = HashMapFactory.make();
				JSONArray nodes = parseTreeJson
					.getJSONObject("graph")
					.getJSONArray("nodes");
				for(int i = 0; i < nodes.length(); i++) {
					JSONObject node = nodes.getJSONObject(i);
					idToNode.put(node.getInt("id"), node);
				}
				parseTreeJson
					.getJSONObject("graph")
					.getJSONArray("edges")
					.forEach(n -> {
						JSONObject e = (JSONObject)n;
						JSONArray edge = e.getJSONArray("between");
						JSONObject src = idToNode.get(edge.getInt(0));
						JSONObject dst = idToNode.get(edge.getInt(1));
						if (! forward.containsKey(src)) {
							forward.put(src, HashSetFactory.make());
						}
						forward.get(src).add(dst);
						if (! backward.containsKey(dst)) {
							backward.put(dst, HashSetFactory.make());
						}
						backward.get(dst).add(src);
					});
			}

			@Override
			public Iterator<JSONObject> getPredNodes(JSONObject n) {
				return backward.get(n).iterator();
			}

			@Override
			public int getPredNodeCount(JSONObject n) {
				return backward.get(n).size();
			}

			@Override
			public Iterator<JSONObject> getSuccNodes(JSONObject n) {
				if (forward.containsKey(n)) {
					return forward.get(n).iterator();
				} else {
					return EmptyIterator.instance();
				}
			}

			@Override
			public int getSuccNodeCount(JSONObject N) {
				return forward.get(N).size();
			}

			@Override
			public void addEdge(JSONObject src, JSONObject dst) {
				throw new UnsupportedOperationException();
			}

			@Override
			public void removeEdge(JSONObject src, JSONObject dst) throws UnsupportedOperationException {
				throw new UnsupportedOperationException();
			}

			@Override
			public void removeAllIncidentEdges(JSONObject node) throws UnsupportedOperationException {
				throw new UnsupportedOperationException();
			}

			@Override
			public void removeIncomingEdges(JSONObject node) throws UnsupportedOperationException {
				throw new UnsupportedOperationException();
			}

			@Override
			public void removeOutgoingEdges(JSONObject node) throws UnsupportedOperationException {
				throw new UnsupportedOperationException();
			}

			@Override
			public boolean hasEdge(JSONObject src, JSONObject dst) {
				return forward.get(src).contains(dst);
			}

			@Override
			public IntSet getSuccNodeNumbers(JSONObject node) {
				MutableIntSet ns = IntSetUtil.make();
				getSuccNodes(node).forEachRemaining(s -> ns.add(getNumber(s)));
				return ns;
			}

			@Override
			public IntSet getPredNodeNumbers(JSONObject node) {
				MutableIntSet ns = IntSetUtil.make();
				getPredNodes(node).forEachRemaining(s -> ns.add(getNumber(s)));
				return ns;
			}
			
		};
	}

	@Override
	protected NumberedNodeManager<JSONObject> getNodeManager() {
		return nodes;
	}

	@Override
	protected NumberedEdgeManager<JSONObject> getEdgeManager() {
		return edges;
	}
}
