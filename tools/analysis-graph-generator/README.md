This is WALA program analysis support for Project CodeNet

## setup

run ./build.sh to download WALA and build the analysis suport

## analysis graphs for GNNs

# build graph files for GNN using the SDG
java -cp target/AnalysisGraphGenerator-0.0.1-SNAPSHOT.jar -DoutputDir=<dir for GNN files> -DgraphLabel=<graph label> -DSDG=true com.ibm.wala.codeNet.WalaToGNNFiles -sourceDir <jav dir or file> -mainClass L<main class name>

# build graph files for GNN using the IPCFG
java -cp target/AnalysisGraphGenerator-0.0.1-SNAPSHOT.jar -DoutputDir=<dir for GNN files> -DgraphLabel=<graph label> -DSDG=true com.ibm.wala.codeNet.WalaToGNNFiles -sourceDir <jav dir or file> -mainClass L<main class name>
