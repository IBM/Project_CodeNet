# get WALA
git clone https://github.com/wala/WALA
cd WALA
git checkout java11
./gradlew clean assemble publishToMavenLocal
cd ..

mvn clean install


