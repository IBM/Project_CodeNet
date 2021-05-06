package com.ibm.ai4code.parser.commons;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.Stack;

import org.antlr.v4.runtime.tree.TerminalNodeImpl;



import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.Vocabulary;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.RuleNode;



public class SPTNode implements TreeNodeIntf<SPTNode>{
	private String name="";
	private String label=""; // weiz 2020-10-29, the label that we will use to build trees similar to the ones in Aroma
	private String ruleName="";
	private int ruleIndex=-1; // weiz 2021-03-05, this is used to encode rule name so that it can be consumed by NN
	private boolean isLeaf = true;
	private boolean reservedWordFlag=false; // weiz 2020-10-29, used updated when labeling
	private int bfsIdx =  0; // weiz 2021-03-04, renamed from idx to bfsIdx, as we will also add dfsIdx later
	private int dfsIdx = 0; // weiz 2021-03-04, required for the DAGNN model
	private int tokenIdx = 0; // weiz 2020-11-18 add the token index, so users can use .json file to locate parent-children relationship
	private int depth = 0;
	
	private ArrayList<SPTNode> children = null;
	private SPTNode parentNode = null;
	
	// static fields
	private static int tokenIdxMax=-1; // weiz 2020-11-18 remember the 
	public SPTNode() {
		
	}
	public SPTNode (String name, boolean isLeaf) {
		this.name = name;
		this.label = name;
		this.isLeaf = isLeaf;
	}
	public SPTNode(String name, boolean isLeaf, ArrayList<SPTNode> children) {
		this.name = name;
		this.label = name;
		this.isLeaf = isLeaf;
		this.children = children;
		if(children == null) {
			assert(this.isLeaf);
		}else {
			assert(!this.isLeaf);
			assert(children.size() > 0);
		}
	}
	public void setParentNode(SPTNode parentNode) {
		this.parentNode = parentNode;
	}
	public void addChildNode(SPTNode node) {
		
		children.add(node);
		this.isLeaf = false;
	}
	public int getChildCnt() {
		if(null == this.children) {
			return 0;
		}
		return children.size();
	}
	public ArrayList<SPTNode> getChildren(){
		return this.children;
	}
	
	public SPTNode getChildAtIdx(int idx) {
		return this.children.get(idx);
	}
	
	public void setChildren(ArrayList<SPTNode> children) {
		this.children = children;
	}
	public void setBFSIdx(int idx) {
		this.bfsIdx = idx;
	}
	public int getBFSIdx() {
		return this.bfsIdx;
	}
	
	public void setDFSIndex(int idx) {
		this.dfsIdx = idx;
	}
	
	public int getDFSIndex() {
		return this.dfsIdx;
	}
	
	public void setRuleIndex(int ruleIndex) {
		this.ruleIndex = ruleIndex;
	}
	public int getRuleIndex() {
		return this.ruleIndex;
	}
	
	public void setTokenIdx(int tIdx) {
		this.tokenIdx = tIdx;
	}
	public int getTokenIdx() {
		return this.tokenIdx; 
	}
	
	public void setDepth(int depth) {
		this.depth  = depth;
	}
	public int getDepth() {
		return this.depth;
	}
	
	public void setReservedWordFlag(boolean flag) {
		this.reservedWordFlag = flag;
	}
	public boolean getReservedWordFlag() {
		return this.reservedWordFlag;
	}
	
	/**
	 * just simplify some non-leaf node, if it has only one child, then it will become the simplified version of its child,
	 * recursively done so that only leaf nodes and non-leaf nodes have more than 1 child will survive, with parents nodes being updated correctly
	 * After simplifying, two invariants are kept:
	 * (1) Out degree of each non-leaf node is greater than 1
	 * (2) Out degree of each non-leaf node is the same as itself prior to simplification
	 */
	public static SPTNode simplify(SPTNode self, SPTNode parent) {
		if(self.isLeaf) {
			return self;
		}else {
			if(self.getChildCnt() == 1) {
				SPTNode childNode = self.getChildAtIdx(0);
				SPTNode simplifiedNode = simplify(childNode, self);
				simplifiedNode.setParentNode(self); // recursively makes the surviving nodes update its parent 
				return simplifiedNode;
			}else {
				ArrayList<SPTNode> simplifiedChildren = new ArrayList<SPTNode>();
				for(SPTNode childNode : self.children) {
					SPTNode simplifiedChildNode = simplify(childNode, self);
					simplifiedChildNode.setParentNode(self);
					simplifiedChildren.add(simplifiedChildNode); // recursively makes the surviving nodes update its parent
				}
				self.setChildren(simplifiedChildren);
				return self;
			}
		}
		
	}
	/**
	 * depth-first building tree
	 * @param tree
	 * @param parent
	 * @param ruleNames
	 * @param vocabulary
	 * @return
	 */
	public static SPTNode buildSPTNode(ParseTree tree, SPTNode parent, String [] ruleNames, Vocabulary vocabulary) {
		if (tree instanceof TerminalNodeImpl) {
			TerminalNodeImpl tni = (TerminalNodeImpl) tree;
			String name = tni.getText(); // weiz 2020-10-29, get the text, which we hope will be compared against the reserved words
			// TODO need to check if it is in the reserved word list
			SPTNode self = new SPTNode(name, true, null);
			Token token = tni.getSymbol(); // weiz 2020-11-17, get token name
			self.tokenIdx = token.getTokenIndex(); // weiz 2021-01-19, token idx is only meaningful for tokens
			if(tokenIdxMax < self.tokenIdx) {
				tokenIdxMax = self.tokenIdx;
			}
			//self.ruleName = vocabulary.getSymbolicName(token.getType());	// leaf node's rule name is the type name
			self.ruleIndex = token.getType(); // weiz 2021-03-04 type of token
			self.ruleName = vocabulary.getDisplayName(token.getType());	// leaf node's rule name is the type name
			self.setParentNode(parent);
			
			return self;
		}else {
			assert (tree instanceof RuleNode);
			RuleNode rn = (RuleNode) tree;
			//Utils.showHierarchy(rn.getClass());
			/*System.out.println(rn.getClass());
			System.out.println(ruleNames[rn.getRuleContext().getRuleIndex()]);
			System.out.println("----------");*/
			SPTNode self = new SPTNode("nonleaf", false, new ArrayList<SPTNode>());
			self.ruleIndex = rn.getRuleContext().getRuleIndex(); // weiz 2021-03-04, add the rule index
			self.ruleName = ruleNames[rn.getRuleContext().getRuleIndex()]; // weiz 2020-11-16, add rule names for non-leaf node
			int childCnt = tree.getChildCount();
			for(int i = 0; i < childCnt; ++i) {
				SPTNode childNode = buildSPTNode(tree.getChild(i), self, ruleNames, vocabulary);
				self.addChildNode(childNode);
			}
			self.setParentNode(parent);
			return self;
		}
	}
	
	/**
	 * Count how many nodes (including leaves and non-leaves) in the tree
	 * @param root
	 * @return
	 */
	public static int count(SPTNode root) {
		if(root.isLeaf) {
			return 1;
		}else {
			int cnt=1; // already included itself
			ArrayList<SPTNode> children = root.getChildren();
			for(SPTNode child: children) {
				cnt+=count(child);
			}
			return cnt;
		}
	}
	
	/**
	 * index the tree via layer-wise traversal (i.e. BFS)
	 * @param root
	 */
	public static Queue<SPTNode> bfsIndexing(SPTNode root) {
		Queue<SPTNode> queue = new LinkedList<SPTNode>();
		Queue<SPTNode> shadowQueue = new LinkedList<SPTNode>();
		queue.add(root);
		// step1, layer-wise traversal and build the printQueue
		while (!queue.isEmpty()) {
			SPTNode node = queue.remove();
			int idx = shadowQueue.size();
			node.bfsIdx = idx; // BFS index
			if(!node.isLeaf) {
				node.tokenIdx = ++(tokenIdxMax); // weiz 2020-11-18, generate tokenIdx for json file so that user can locate parent idx for token
				// weiz 2021-01-19, for non-terminal node, this tokenIdx doesn't make much sense except it carries
				// the relative BFS position to other non-terminal nodes in the parse tree. In the output of Json file, we 
				// don't output tokenIdx for non-terminal nodes (i.e. rule nodes)
			}
			shadowQueue.add(node);
			int depth = node.depth;
			ArrayList<SPTNode> children = node.getChildren();
			if (children != null) { // weiz 2020-10-29 the children could be null, because it could be a leaf node
				for (SPTNode child : children) {
					child.depth = depth+1;
					queue.add(child);
				}
			}

		}
		//System.out.println("Queue Size: " + shadowQueue.size());
		return shadowQueue;
				
	}
	
	
	/**
	 * 
	 * @param root
	 * @return number of nodes
	 */
	public static int dfsIndexing(SPTNode root) {
		Stack<SPTNode> stack = new Stack<SPTNode>();
		stack.push(root);
		int index = 0;
		while(!stack.isEmpty()) {
			SPTNode node = stack.pop();
			node.dfsIdx = index++;
			if(!node.isLeaf) {
				ArrayList<SPTNode> children = node.getChildren();
				for(int idx = children.size()-1; idx>=0;idx--) { // note we push children from right to left in the stack, so when it pops, it pops from right to left
					stack.push(children.get(idx));
				}
			}
		}
		return index;
	}
	
	/**
	 * A Facebook Aroma type labeling scheme
	 * @param root
	 * @param rwdi
	 */
	public static void aromaLabeling(SPTNode root, ReservedWordDeciderI rwdi) {
		// step 1, just to figure out which ones that are in the reserved word list 
		aromaLabelingStageOne(root, rwdi);
		
		// step 2, to label each non-leaf node 
		aromaLabelingStageTwo(root);
	}
	/**
	 * AromaLabeling stage one, just find out all the reserved words
	 * @param root
	 * @param rwdi
	 */
	private static void aromaLabelingStageOne(SPTNode root, ReservedWordDeciderI rwdi) {
		if(root.isLeaf) {
			if(rwdi.isReserved(root.name)) {
				root.reservedWordFlag = true;
			}
			root.label = root.name; // a leaf node (i.e., token) always gets to keep its name as label
			
		}else {
			ArrayList<SPTNode> children = root.getChildren();
			for(SPTNode child: children) {
				aromaLabelingStageOne(child, rwdi);
			}
			
		}
	}
	
	private static void aromaLabelingStageTwo(SPTNode root) {
		if(root.isLeaf) {
			return;
		}else {
			String label="";
			ArrayList<SPTNode> children = root.getChildren();
			for(SPTNode child : children) {
				if(child.reservedWordFlag) {
					label+=child.label;
				}else {
					label +="#";
				}
			}
			root.label = label;
			for(SPTNode child:children) {
				aromaLabelingStageTwo(child);
			}
		}
		
	}
	
	/**
	 * reset static fields (e.g., tokenIdxMax) before building SPT tree
	 */
	public static void resetStaticFields() {
		tokenIdxMax = -1;
	}
	
	public String getLabel() {
		return this.label;
		//return this.label+ " ("+this.dfsIdx + ","+ this.depth+")";
		/*if(this.isLeaf) {
			return this.label;
		}else {
			return this.ruleName;
		}*/
	}
	
	public String getRuleName() {
		return this.ruleName;
	}
	
	public String getType() {
		if(this.isLeaf) {
			return "Token";
		}else {
			return "Rule";
		}
	}
	
	
	
	
	public String toString(){
		//return this.name+"(" + idx+","+ depth+")";
		//return this.name;
		if(this.isLeaf) {
			return this.label+":" + this.tokenIdx+ ":"+this.ruleName;
		}
		return this.label+":"+this.tokenIdx+":"+this.ruleName;
	}
	
}
