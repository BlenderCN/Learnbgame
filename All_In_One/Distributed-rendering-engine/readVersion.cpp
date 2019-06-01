/*
 Author : Rupinder Singh
 Test prog to read version from blender file	
*/
#include<iostream>
#include<fstream>
using namespace std;
int main(){
	ifstream fin;
	char version[3];

	fin.open("bfile.blend");
	fin.seekg(9);

	fin.read(version,3);

	cout<<version;

	fin.close();
	cout<<endl;
	return 0;
}