package com.ibm.ai4code.parser.commons;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Queue;


public class TreePrinter<T extends TreeNodeIntf<T>> {
	private T root;
	private Queue<TreePrinterNode> queue;
	private Queue<TreePrinterNode> printQueue;
	public TreePrinter(T root) {
		this.root = root;
		TreePrinterNode tpn= new TreePrinterNode(root, 0);
		this.queue = new LinkedList<TreePrinterNode>();
		this.printQueue = new LinkedList<TreePrinterNode>();
		queue.add(tpn);
	}
	public void print() {
		// step1, layer-wise traversal and build the printQueue
		while(!queue.isEmpty()) {
			TreePrinterNode tpn = queue.remove();
			printQueue.add(tpn);
			int level = tpn.getLevel();
			ArrayList<T> children = tpn.node.getChildren();
			if(children != null) {
				for(T child: children) {
					tpn = new TreePrinterNode(child, level+1);
					queue.add(tpn);
				}
			}
			
		}
		System.out.println("Queue Size: " + printQueue.size());
		// step 2, print elements in printQueue
		int level=0;
		while(!printQueue.isEmpty()) {
			TreePrinterNode tpn = printQueue.remove();
			if(tpn.level > level) {
				level = tpn.level;
				System.out.println();
			}
			System.out.print(tpn.node+"\t");
		}
	}
	
	private class TreePrinterNode{
		T node;
		int level;
		public TreePrinterNode() {
			this.node = null;
			this.level = -1;
		}
		public TreePrinterNode(T node, int level) {
			this.node = node;
			this.level = level;
		}
		public int getLevel() {
			return this.level;
		}
		public void setLevel(int level) {
			this.level = level;
		}
		
	}
}
