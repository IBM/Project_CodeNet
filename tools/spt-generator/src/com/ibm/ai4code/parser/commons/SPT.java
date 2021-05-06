package com.ibm.ai4code.parser.commons;

import java.util.Queue;

import org.antlr.v4.runtime.Vocabulary;
import org.antlr.v4.runtime.tree.ParseTree;

/**
 * Simplified ParseTree
 * @author weiz
 *
 */
public class SPT {
	private SPTNode root;
	private Queue<SPTNode> shadowQueue = null;
	private int numNodes; // weiz 2021-03-05, for GNN training
	private int numEdges; // weiz 2021-03-05
	private String srcFileName; // weiz 2021-03-06, add file name
	public SPT() {
		root = null;
	}
	public SPT(SPTNode root){
		this.root = root;
	}
	// weiz 2020-11-17 add support for ruleNames and vocabulary
	public SPT(ParseTree tree, String [] ruleNames, Vocabulary vocabulary) {
		SPTNode.resetStaticFields(); // weiz 2020-11-18, add the reset static fields (clear out tokenIdxMax)
		this.root = SPTNode.buildSPTNode(tree, null, ruleNames, vocabulary);
	}
	
	public SPTNode getRoot() {
		return this.root;
	}
	
	public void simplify() {
		SPTNode.simplify(root, null);
	}
	
	public int count() {
		return SPTNode.count(root);
	}
	public void indexing() {
		this.shadowQueue = SPTNode.bfsIndexing(root);
		this.numNodes = SPTNode.dfsIndexing(root); // weiz, add dfs index
		this.numEdges = this.numNodes - 1;
	}
	
	public int getNumNodes() {
		return this.numNodes;
	}
	public int getNumEdges() {
		return this.numEdges;
	}
	public void setSrcFileName(String srcFileName) {
		this.srcFileName = srcFileName;
	}
	public String getSrcFileName() {
		return this.srcFileName;
	}
	
	
	public void labeling(ReservedWordDeciderI rwdi) {
		SPTNode.aromaLabeling(root, rwdi);
	}
	
	public Queue<SPTNode> getLayerWiseTraversalQueue(){
		assert(shadowQueue != null); // when this method queue is called, indexing() must have been called
		return shadowQueue;
	}
	
	
	
	
	
	
}
