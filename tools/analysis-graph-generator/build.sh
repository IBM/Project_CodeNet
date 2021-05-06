# get WALA
git clone https://github.com/wala/WALA
cd WALA
git checkout java11
./gradle clean build publishToMavenLocal
cd ..

mvn clean install


