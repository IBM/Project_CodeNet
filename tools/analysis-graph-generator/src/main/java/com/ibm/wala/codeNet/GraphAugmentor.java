package com.ibm.wala.codeNet;

import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import com.ibm.wala.cast.java.ecj.util.SourceDirCallGraph;
import com.ibm.wala.cast.java.ipa.callgraph.JavaSourceAnalysisScope;
import com.ibm.wala.cast.java.ipa.modref.AstJavaModRef;
import com.ibm.wala.cast.loader.AstMethod;
import com.ibm.wala.cast.loader.AstMethod.DebuggingInformation;
import com.ibm.wala.cast.tree.CAstSourcePositionMap.Position;
import com.ibm.wala.cast.util.SourceBuffer;
import com.ibm.wala.ipa.callgraph.CGNode;
import com.ibm.wala.ipa.callgraph.CallGraphBuilderCancelException;
import com.ibm.wala.ipa.callgraph.propagation.InstanceKey;
import com.ibm.wala.ipa.callgraph.propagation.PropagationCallGraphBuilder;
import com.ibm.wala.ipa.cha.ClassHierarchyException;
import com.ibm.wala.ipa.slicer.Dependency;
import com.ibm.wala.ipa.slicer.NormalStatement;
import com.ibm.wala.ipa.slicer.ParamCallee;
import com.ibm.wala.ipa.slicer.ParamCaller;
import com.ibm.wala.ipa.slicer.SDG;
import com.ibm.wala.ipa.slicer.Slicer;
import com.ibm.wala.ipa.slicer.Statement;
import com.ibm.wala.ssa.SSAInstruction;
import com.ibm.wala.util.collections.HashMapFactory;
import com.ibm.wala.util.graph.Graph;
import com.ibm.wala.util.graph.GraphSlicer;

public class GraphAugmentor {

	public static void main(String... args) throws ClassHierarchyException, IllegalArgumentException, CallGraphBuilderCancelException, IOException {
		NodeFinder nf = new NodeFinder(System.getProperty("tokenFile"), System.getProperty("parseTreeFile"));
				
		(new SourceDirCallGraph()).doit(args, (cg, builder, time) -> { 
		    SDG<? extends InstanceKey> sdg =
		    		new SDG<>(
		                cg,
		                ((PropagationCallGraphBuilder)builder).getPointerAnalysis(),
		                new AstJavaModRef<>(),
		                Slicer.DataDependenceOptions.NO_HEAP_NO_EXCEPTIONS,
		                Slicer.ControlDependenceOptions.NO_EXCEPTIONAL_EDGES);

			Graph<Statement> srcSdg = GraphSlicer.prune(sdg, 
				n -> n.getNode().getMethod().getReference().getDeclaringClass().getClassLoader() == JavaSourceAnalysisScope.SOURCE);

			Map<Dependency, JSONArray> sdgEdgesForSpt = HashMapFactory.make();
			
			srcSdg.forEach(srcNode -> { 
				JSONObject srcJson = findNodeForStatement(nf, srcNode);
				if (srcJson != null) {
					srcSdg.getSuccNodes(srcNode).forEachRemaining(dstNode -> { 
						JSONObject dstJson = findNodeForStatement(nf, dstNode);
						if (dstJson != null && !srcJson.equals(dstJson)) {
							JSONArray ea = new JSONArray(new int[] {srcJson.getInt("id"), dstJson.getInt("id")});
							JSONObject e = new JSONObject();
							e.put("between", ea);
							sdg.getEdgeLabels(srcNode, dstNode).forEach(l -> {
								if (! sdgEdgesForSpt.containsKey(l)) {
									sdgEdgesForSpt.put(l, new JSONArray());
								}
								sdgEdgesForSpt.get(l).put(e);
							});
						}
					});
				}
			});
			
			sdgEdgesForSpt.entrySet().forEach(es -> {
				try {
					JSONObject json = ((JSONObject)new JSONTokener(new FileInputStream(System.getProperty("parseTreeFile"))).nextValue());
					json.getJSONObject("graph").put("edges", es.getValue());
					json.getJSONObject("graph").put("num-of-edges", es.getValue().length());
					try (FileWriter f = new FileWriter(System.getProperty("parseTreeFile") + "." + es.getKey())) {
						json.write(f, 2, 0);
					} 
				} catch (JSONException | IOException e) {
					assert false : e;
				}
			});
		});
	}

	private static JSONObject findNodeForStatement(NodeFinder nf, Statement srcNode) {
		Position srcPos = getPosition(srcNode);
		
		JSONObject srcJson = nf.getCoveringNode(srcPos.getFirstOffset(), srcPos.getLastOffset());
		
		try {
			System.err.println(srcJson.getInt("id") + " : " + new SourceBuffer(srcPos) + " : " + srcNode);
		} catch (IOException e) {
			
		}
		
		return srcJson;
	}

	static Position getPosition(Statement srcNode) {
		Position srcPos;
		CGNode srcCG = srcNode.getNode();
		DebuggingInformation debugInfo = ((AstMethod)srcCG.getMethod()).debugInfo();
		if (srcNode.getKind() == Statement.Kind.NORMAL) {
			SSAInstruction srcInst = ((NormalStatement)srcNode).getInstruction();
			srcPos = debugInfo.getInstructionPosition(srcInst.iIndex());
		} else if (srcNode.getKind() == Statement.Kind.PARAM_CALLER) findParamCaller: {
			SSAInstruction call = ((ParamCaller)srcNode).getInstruction();
			int vn = ((ParamCaller)srcNode).getValueNumber();
			for(int i = 0; i < call.getNumberOfUses(); i++) {
				if (call.getUse(i) == vn) {
					srcPos = debugInfo.getOperandPosition(call.iIndex(), i);
					break findParamCaller;
				}
			}
			assert false;
			return null;
		} else if (srcNode.getKind() == Statement.Kind.PARAM_CALLEE) {
			int arg = ((ParamCallee)srcNode).getValueNumber() - 1;
			srcPos = debugInfo.getParameterPosition(arg);
		} else {
			return null;
		}
		return srcPos;
	}
}
