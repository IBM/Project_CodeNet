package com.ibm.wala.codeNet;

import java.io.FileReader;
import java.io.IOException;
import java.util.Comparator;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;
import java.util.SortedMap;
import java.util.TreeMap;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.json.JSONException;
import org.json.JSONObject;

import com.ibm.wala.util.collections.HashMapFactory;
import com.ibm.wala.util.collections.HashSetFactory;
import com.ibm.wala.util.collections.Pair;

public class NodeFinder {

	private final Map<Integer, Pair<Integer, Integer>> tokenMap = HashMapFactory.make();
	private final Map<JSONObject, Pair<Integer, Integer>> locations = HashMapFactory.make();
	private final SortedMap<Integer,Set<JSONObject>> offsetToNodes = new TreeMap<>(new Comparator<Integer>() {
		@Override
		public int compare(Integer o1, Integer o2) {
			return o1 - o2;
		}
	});

	private WalaSPTGraph parseTree;

	NodeFinder(String tokenFile, String parseTreeFile) throws JSONException, IOException {
		CSVParser csvParser = CSVFormat.DEFAULT.withHeader().parse(new FileReader(tokenFile));
		for (CSVRecord token : csvParser) {
			int id = Integer.valueOf(token.get("seqnr"));
			int startOffset = Integer.valueOf(token.get("start"));
			int endOffsetInclusive = Integer.valueOf(token.get("stop"));
			tokenMap.put(id, Pair.make(startOffset, endOffsetInclusive));
		}

		parseTree = new WalaSPTGraph(parseTreeFile);
	}

	private Pair<Integer,Integer> location(JSONObject node) {
		Pair<Integer,Integer> result;
		if (locations.containsKey(node)) {
			return locations.get(node);
		} else {
			if (node.getString("node-type").equals("Token")) {
				result = tokenMap.get(node.getInt("token-id"));
			} else {
				int start = Integer.MAX_VALUE;
				int end = Integer.MIN_VALUE;
				Iterator<JSONObject> ss = parseTree.getSuccNodes(node);
				while (ss.hasNext()) {
					Pair<Integer,Integer> s = location(ss.next());
					if (s.fst < start) {
						start = s.fst;
					}
					if (s.snd > end) {
						end = s.snd;
					}
				}
				result = Pair.make(start, end);
			}
			locations.put(node, result);
			for(int i = result.fst; i <= result.snd; i++) {
				if (! offsetToNodes.containsKey(i)) {
					offsetToNodes.put(i,  HashSetFactory.make());
				}

				offsetToNodes.get(i).add(node);
			}
			return result;
		}
	}

	public JSONObject getCoveringNode(int startOffset, int endOffset) {
		JSONObject node = parseTree.getNode(parseTree.root);
		Pair<Integer,Integer> loc = location(node);
		descend: while(loc.fst <= startOffset && loc.snd >= endOffset) {
			Iterator<JSONObject> children = parseTree.getSuccNodes(node);
			while (children.hasNext()) {
				JSONObject c = children.next();
				Pair<Integer,Integer> cl = location(c);
				if (cl.fst <= startOffset && cl.snd >= endOffset) {
					loc = cl;
					node = c;
					continue descend;
				}
			}
			
			return node;
		}
		
		assert false;
		return null;
	}
}
