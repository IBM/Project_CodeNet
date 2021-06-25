# get WALA
git clone https://github.com/wala/WALA
cd WALA
git checkout java11
./gradlew clean build publishToMavenLocal
cd ..

mvn clean install


