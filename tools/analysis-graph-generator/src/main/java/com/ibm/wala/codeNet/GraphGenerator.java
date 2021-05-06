package com.ibm.wala.codeNet;

import java.io.FileWriter;
import java.io.IOException;
import java.util.Comparator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map.Entry;
import java.util.SortedSet;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.TreeSet;
import java.util.function.BiFunction;
import java.util.function.BinaryOperator;
import java.util.stream.StreamSupport;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import com.ibm.wala.cast.java.ecj.util.SourceDirCallGraph;
import com.ibm.wala.cast.java.ipa.callgraph.JavaSourceAnalysisScope;
import com.ibm.wala.ipa.callgraph.CallGraphBuilderCancelException;
import com.ibm.wala.ipa.cha.ClassHierarchyException;
import com.ibm.wala.ssa.SSACFG;
import com.ibm.wala.util.graph.NumberedGraph;

public class GraphGenerator {

	static class OrderedJSONObject extends JSONObject {
		private final List<String> keys = new LinkedList<>();
		
		@Override
		protected SortedSet<Entry<String, Object>> entrySet() {
			TreeSet<Entry<String, Object>> set = new TreeSet<Entry<String, Object>>(new Comparator<Entry<String, Object>>() {
				@Override
				public int compare(Entry<String, Object> o1, Entry<String, Object> o2) {
					return keys.indexOf(o2.getKey()) - keys.indexOf(o1.getKey());
				} 
			});
			set.addAll(super.entrySet());
			return set;
		}

		@Override
		public JSONObject put(String key, Object value) throws JSONException {
			if (keys.contains(key)) {
				keys.remove(key);
			}
			
			keys.add(0, key);
			
			return super.put(key, value);
		}
	
		
	}
	
	@FunctionalInterface
	interface NodeLabel<T> {
		String label(T n);
	}
	
	@FunctionalInterface
	interface EdgeLabel<T> {
		String label(T a, T b);
	}
	
	private static final BinaryOperator<JSONArray> arrayAppend = (a1, a2) -> { 
		JSONArray a = new JSONArray();
		a1.forEach(x -> a.put(x));
		a2.forEach(x -> a.put(x));
		return a;
	};

	private static final BiFunction<JSONArray, JSONObject, JSONArray> arrayAdd = (a, jn) -> { 
		a.put(jn); return a; 
	};

	public static <T> JSONObject toJSON(String method, NumberedGraph<T> G, T root, NodeLabel<T> nodeLabels, EdgeLabel<T> edgeLabels) {
		JSONObject outer = new OrderedJSONObject();
		JSONObject jg = new OrderedJSONObject();
		outer.put("graph", jg);
		outer.put("method", method);
		jg.put("version", "1.0");
		jg.put("directed", true);
		jg.put("root", G.getNumber(root));
		jg.put("nodes", 
				G.stream().map(n -> {
					JSONObject jn = new OrderedJSONObject();
					jn.put("id", G.getNumber(n));
					jn.put("label", nodeLabels.label(n));
					return jn;
				}).reduce(new JSONArray(), arrayAdd, arrayAppend));
		jg.put("edges", 
				G.stream().flatMap(n -> { 
					return StreamSupport.stream(
						Spliterators.spliterator(G.getSuccNodes(n), G.getSuccNodeCount(n), Spliterator.ORDERED),
						false).map(s -> { 
							JSONObject eo = new OrderedJSONObject();
							JSONArray edge = new JSONArray(); 
							edge.put(G.getNumber(n));
							edge.put(G.getNumber(s));
							eo.put("between", edge);
							eo.put("label", edgeLabels.label(n, s));
							return eo;
						});
				}).reduce(new JSONArray(), arrayAdd, arrayAppend));

		return outer;
	}

	public static void main(String... args) throws ClassHierarchyException, IllegalArgumentException, CallGraphBuilderCancelException, IOException {
		(new SourceDirCallGraph()).doit(args, (cg, builder, time) -> { 
			cg.stream()
				.filter(n -> n.getMethod().getDeclaringClass().getClassLoader().getReference().equals(JavaSourceAnalysisScope.SOURCE))
				.map(n -> { 
					SSACFG cfg = n.getIR().getControlFlowGraph();
					return toJSON(n.getMethod().getSignature(),
						cfg, 
						cfg.entry(), 
						bb -> { return String.valueOf(bb.getNumber()); }, 
						(bb, sb) -> { return bb.getNumber() + " -> " + sb.getNumber(); });
				}).forEach(jcfg -> { 
					String methodName = jcfg.getString("method");
					System.out.println("method " + methodName);
					try {
						jcfg.write(new FileWriter("/tmp/" + methodName.replace('/',  '_').replace(' ', '_').replace('.', '_') + ".json"), 2, 0).flush();
					} catch (JSONException | IOException e) {
						e.printStackTrace();
					} 
				});
			}
		);
	}
}
