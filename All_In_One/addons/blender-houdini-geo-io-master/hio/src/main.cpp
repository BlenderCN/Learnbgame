#include <math.h>
#include <iostream>
#include "hio.h"

using namespace hio;

#define CATCH_CONFIG_RUNNER

#include <catch2/catch.hpp>

TEST_CASE("load and save", "[hio]") {
	Geometry geo;
	REQUIRE(geo.load("geo/box.bgeo"));
	REQUIRE(geo.getNumPoints() == 8);
	REQUIRE(geo.getNumVertices() == 24);
	REQUIRE(geo.getNumPrimitives() == 6);

	REQUIRE(geo.save("geo/out_box.bgeo"));

	Geometry geo2;
	REQUIRE(geo2.load("geo/out_box.bgeo"));

	REQUIRE(geo.getNumPoints() == geo2.getNumPoints());
	REQUIRE(geo.getNumVertices() == geo2.getNumVertices());
	REQUIRE(geo.getNumPrimitives() == geo2.getNumPrimitives());
}

TEST_CASE("clear", "[hio]") {
	Geometry geo;
	REQUIRE(geo.load("geo/box.bgeo"));

	geo.clear();

	REQUIRE(geo.save("geo/out_clear.bgeo"));

	REQUIRE(geo.getNumPoints() == 0);
	REQUIRE(geo.getNumVertices() == 0);
	REQUIRE(geo.getNumPrimitives() == 0);

	REQUIRE(geo.pointAttribs().size() == 1);
	REQUIRE(geo.vertexAttribs().size() == 0);
	REQUIRE(geo.primAttribs().size() == 0);
	REQUIRE(geo.globalAttribs().size() == 0);
}

TEST_CASE("double load", "[hio]") {
	Geometry geo;
	REQUIRE(geo.load("geo/box.bgeo"));

	Geometry geo2;
	REQUIRE(geo2.load("geo/box.bgeo"));
	REQUIRE(geo2.load("geo/box.bgeo"));

	REQUIRE(geo.getNumPoints() == geo2.getNumPoints());
	REQUIRE(geo.getNumVertices() == geo2.getNumVertices());
	REQUIRE(geo.getNumPrimitives() == geo2.getNumPrimitives());
}

TEST_CASE("points" "[hio]") {
	Geometry geo;

	auto pt = geo.createPoint();
	auto P = pt.position(geo);
	REQUIRE((P.x() == 0 && P.y() == 0 && P.z() == 0));

	pt.setPosition(geo, Vector3(1, 2, 3));
	P = pt.position(geo);
	REQUIRE((P.x() == 1 && P.y() == 2 && P.z() == 3));

	{
		for (int i = 0; i < 10; i++)
		{
			auto pt = geo.createPoint();
			REQUIRE(pt.number() == i + 1);
		}

		REQUIRE(geo.getNumPoints() == 11);
	}

	{
		auto pts = geo.createPoints(10);
		REQUIRE(pts.size() == 10);
		REQUIRE(geo.getNumPoints() == 21);
	}
}

TEST_CASE("polygon" "[hio]") {
	Geometry geo;

	auto poly = geo.createPolygon();
	REQUIRE(geo.getNumPrimitives() == 1);

	poly.setIsClosed(true);
	REQUIRE(poly.isClosed() == true);

	poly.setIsClosed(false);
	REQUIRE(poly.isClosed() == false);

	auto poly2 = poly;

	poly.setIsClosed(true);
	REQUIRE(poly2.isClosed() == true);

	for (int i = 0; i < 10; i++)
	{
		auto pt = geo.createPoint();
		pt.setPosition(geo, Vector3(i, 0, 0));
		poly.addVertex(pt);
	}

	poly.setIsClosed(false);

	REQUIRE(poly.vertexCount() == 10);

	REQUIRE(geo.getNumPoints() == 10);
	REQUIRE(geo.getNumPrimitives() == 1);
	REQUIRE(geo.getNumVertices() == 10);

	{
		auto poly = geo.createPolygon();

		for (int i = 0; i < 5; i++)
		{
			auto pt = geo.createPoint();
			pt.setPosition(geo, Vector3(0, i, 1));
			auto vt = poly.addVertex(pt);
		}
		
		REQUIRE(poly.vertexCount() == 5);
	}

	REQUIRE(geo.getNumPoints() == 15);
	REQUIRE(geo.getNumPrimitives() == 2);
	REQUIRE(geo.getNumVertices() == 15);

	{
		std::vector<Vector3> points = {
			{0, 0, 0},
			{1, 0, 0},
			{1, 1, 0},

			{1, 1, 0},
			{0, 1, 0},
			{0, 1, 1},

			{0, 1, 0},
			{0, 1, 1},
			{0, 0, 0},
			{1, 1, 0},
		};

		std::vector<Size> vertex_counts = {3, 3, 4};

		geo.createPolygons(points.size(), points.data(), vertex_counts.size(), vertex_counts.data(), true);
	}

	REQUIRE(geo.getNumPoints() == 25);
	REQUIRE(geo.getNumPrimitives() == 5);
	REQUIRE(geo.getNumVertices() == 25);

	geo.save("geo/out_polygon_test.bgeo");
}

TEST_CASE("createPolygons" "[hio]") {
	Geometry geo;

	std::vector<Vector3> points = {
		{-0.5, -0.5, -0.5},
		{ 0.5, -0.5, -0.5 },
		{ 0.5, -0.5, 0.5 },
		{ -0.5, -0.5, 0.5 },
		{ -0.5, 0.5, -0.5 },
		{ 0.5, 0.5, -0.5 },
		{ 0.5, 0.5, 0.5 },
		{ -0.5, 0.5, 0.5 }
	};

	std::vector<Index> vertices = {
		1, 5, 4, 0, 
		2, 6, 5, 1, 
		3, 7, 6, 2, 
		0, 4, 7, 3, 
		2, 1, 0, 3, 
		5, 6, 7, 4
	};

	std::vector<Size> vertex_counts = {
		4, 4, 4, 4, 4, 4
	};

	auto polys = geo.createPolygons(points.size(), points.data(),
		vertices.size(), vertices.data(),
		vertex_counts.size(), vertex_counts.data(),
		true);
	REQUIRE(polys.size() == 6);

	REQUIRE(geo.getNumPoints() == 8);
	REQUIRE(geo.getNumVertices() == 24);
	REQUIRE(geo.getNumPrimitives() == 6);

	REQUIRE(geo.save("geo/out_create_polygons.bgeo"));
}

TEST_CASE("attributes" "[hio]") {
	Geometry geo;

	{
		auto Cd = geo.addAttrib<float>(AttribType::Point, "Cd", std::vector<float>({ 1, 0, 0, 1 }), TypeInfo::Color);
		REQUIRE(Cd.name() == "Cd");
		REQUIRE(Cd.dataType() == AttribData::Float);
		REQUIRE(Cd.type() == AttribType::Point);
		REQUIRE(Cd.tupleSize() == 4);
		REQUIRE(Cd.typeInfo() == TypeInfo::Color);

		auto N = geo.addAttrib<float>(AttribType::Vertex, "N", std::vector<float>({ 0, 0, 0 }), TypeInfo::Normal);
		REQUIRE(N.name() == "N");
		REQUIRE(N.dataType() == AttribData::Float);
		REQUIRE(N.type() == AttribType::Vertex);
		REQUIRE(N.tupleSize() == 3);
		REQUIRE(N.typeInfo() == TypeInfo::Normal);

		auto X = geo.addAttrib<int>(AttribType::Prim, "X", std::vector<int>({ 10 }), TypeInfo::Value);
		REQUIRE(X.name() == "X");
		REQUIRE(X.dataType() == AttribData::Int);
		REQUIRE(X.type() == AttribType::Prim);
		REQUIRE(X.tupleSize() == 1);
		REQUIRE(X.typeInfo() == TypeInfo::Value);

		auto A = geo.addAttrib<std::string>(AttribType::Global, "A", std::vector<std::string>(1), TypeInfo::Value);
		REQUIRE(A.name() == "A");
		REQUIRE(A.dataType() == AttribData::String);
		REQUIRE(A.type() == AttribType::Global);
		REQUIRE(A.tupleSize() == 1);
		REQUIRE(A.typeInfo() == TypeInfo::Value);

		geo.save("geo/out_attr_empty.bgeo");

		REQUIRE(geo.pointAttribs().size() == 2);
		REQUIRE(geo.vertexAttribs().size() == 1);
		REQUIRE(geo.primAttribs().size() == 1);
		REQUIRE(geo.globalAttribs().size() == 1);

		REQUIRE(geo.findPointAttrib("Cd") == Cd);
		REQUIRE(geo.findVertexAttrib("N") != Cd);
		REQUIRE(geo.findVertexAttrib("N") == N);
		REQUIRE(geo.findPrimAttrib("X") == X);
		REQUIRE(geo.findGlobalAttrib("A") == A);
	}

	{
		auto Cd = geo.addAttrib<float>(AttribType::Point, "Cd", std::vector<float>({ 1, 0, 0, 1 }), TypeInfo::Color);
		REQUIRE(Cd.name() == "Cd");
		REQUIRE(Cd.dataType() == AttribData::Float);
		REQUIRE(Cd.type() == AttribType::Point);
		REQUIRE(Cd.tupleSize() == 4);
		REQUIRE(Cd.typeInfo() == TypeInfo::Color);

		Attrib attr = Cd;

		Attrib_<float>* A = (Attrib_<float>*)&attr;
		REQUIRE(A->name() == "Cd");

		Attrib_<float> B = attr;
		REQUIRE(B.name() == "Cd");

		Attrib_<int> C;
		REQUIRE_THROWS(C = attr);
	}

	{
		Vector3 v;
		std::string s;

		REQUIRE(geo.load("geo/test_attr.bgeo"));

		auto Cd = geo.findPrimAttrib("Cd");
		REQUIRE(Cd);
		REQUIRE_THROWS(Cd.attribValue<float>(&v, -1, 0));
		REQUIRE_THROWS(Cd.attribValue<float>(&v, 0, 30));

		auto str_attr = geo.findPrimAttrib("str_attr");
		REQUIRE(str_attr);
		REQUIRE_THROWS(str_attr.attribValue<std::string>(&s, -1, 0));
		REQUIRE_THROWS(str_attr.attribValue<std::string>(&s, 0, 30));


		std::vector<Vector3> varr(6);
		std::vector<std::string> sarr(6);
		REQUIRE_NOTHROW(Cd.attribValue<float>(varr.data()));
		REQUIRE_NOTHROW(str_attr.attribValue<std::string>(sarr.data()));
	}

	{
		geo.clear();

		auto Cd = geo.addAttrib<float>(AttribType::Point, "Cd", std::vector<float>({ 1, 0, 0, 1 }), TypeInfo::Color);
		
		std::vector<UT_Vector4> arr1;
		std::vector<int> arr2;

		REQUIRE_NOTHROW(Cd.attribValue<float>(&arr1[0], 0, 0));
		REQUIRE_THROWS(Cd.attribValue<int>(&arr2[0], 0, 0));

		geo.createPoint();

		arr1.emplace_back(1, 2, 3, 4);
		REQUIRE_NOTHROW(Cd.setAttribValue<float>(&arr1[0], 0, 1));

		UT_Vector4 v;
		REQUIRE_NOTHROW(Cd.attribValue<float>(&v, 0, 1));
		REQUIRE(v == Vector4(1, 2, 3, 4));

		///

		std::vector<UT_Vector4> arr3;

		geo.createPoint();
		arr1.emplace_back(2, 3, 4, 5);

		REQUIRE_NOTHROW(Cd.setAttribValue<float>(&arr1[0], 0, 2));

		arr3.resize(2);
		REQUIRE_NOTHROW(Cd.attribValue<float>(&arr3[0], 0, 2));

		REQUIRE(arr3[0] == Vector4(1, 2, 3, 4));
		REQUIRE(arr3[1] == Vector4(2, 3, 4, 5));

		geo.save("geo/out_attr_setget.bgeo");
	}

	{
		geo.load("geo/test_attr.bgeo");

		auto missing_attr = geo.findPrimAttrib("missing_attr");
		REQUIRE(!missing_attr);

		auto str_attr = geo.findPrimAttrib("str_attr");
		REQUIRE(str_attr);

		std::vector<std::string> data(str_attr.size());
		str_attr.attribValue<std::string>(data.data());

		for (int i = 0; i < data.size(); i++)
			REQUIRE((data[i] == (std::string("string attribute ") + std::to_string(i))));

		std::string a("xxxxx");
		str_attr.setAttribValue<std::string>(&a, 1, 1);

		std::string b;
		str_attr.attribValue<std::string>(&b, 1, 1);
		REQUIRE(a == b);
	}
}

TEST_CASE("prim_attr" "[hio]") {
	Geometry geo;
	geo.load("geo/test_attr.bgeo");

	auto prim = geo.prim(5);
	REQUIRE(prim.vertexStartIndex() == 20);
	REQUIRE(prim.vertexCount() == 4);

	auto poly = hio::Polygon(prim);
	REQUIRE(poly);

	REQUIRE(poly.vertexCount() == 4);

	auto Cd = geo.findPrimAttrib("Cd");
	Vector3 c;
	poly.attribValue<float>(Cd, &c);
	REQUIRE(c == Vector3(5, 10, 15));

	auto str_attr = geo.findPrimAttrib("str_attr");
	std::string s;
	poly.attribValue<std::string>(str_attr, &s);
	REQUIRE(s == "string attribute 5");
}

TEST_CASE("delete_prims" "[hio]") {
	Geometry geo;
	geo.load("geo/mix_prims.bgeo");

	REQUIRE(geo.getNumPoints() == 20);
	REQUIRE(geo.getNumPrimitives() == 7);

	std::vector<Primitive> prims = { geo.prim(0) };
	geo.deletePrims(prims);

	REQUIRE(geo.getNumPoints() == 8);
	REQUIRE(geo.getNumPrimitives() == 6);

	REQUIRE(geo.prim(0).valid());
	REQUIRE(geo.prim(0).number() == 0);
	REQUIRE(geo.prim(1).valid());
	REQUIRE(geo.prim(1).number() == 1);
}

TEST_CASE("createPoints" "[hio]") {
	Geometry geo;
	std::vector<Vector3> P = {
		{1, 2, 3},
		{4, 5, 6},
		{7, 8, 9}
	};

	geo.createPoints(3, P.data());

	REQUIRE(geo.getNumPoints() == 3);
	REQUIRE(geo.point(0).position(geo) == Vector3(1, 2, 3));
	REQUIRE(geo.point(2).position(geo) == Vector3(7, 8, 9));
}

TEST_CASE("prim_curves" "[hio]") {
	Geometry geo;
	auto B = geo.createBezierCurve(10);
	auto N = geo.createNURBSCurve(10);

	REQUIRE(geo.getNumPoints() == 20);
	REQUIRE(geo.getNumPrimitives() == 2);

	std::vector<Vector3> BP(10), NP(10);
	for (int i = 0; i < 10; i++)
	{
		BP[i] = Vector3(i, 0, 0);
		NP[i] = Vector3(i, 1, 0);
	}

	B.setPositions(BP.data(), 0, BP.size());
	N.setPositions(NP.data(), 0, NP.size());

	REQUIRE(geo.save("geo/out_curves.bgeo"));

	REQUIRE(geo.load("geo/out_curves.bgeo"));

	REQUIRE(geo.getNumPoints() == 20);
	REQUIRE(geo.getNumPrimitives() == 2);

	std::vector<Vector3> BBP(10), NNP(10);

	auto BB = BezierCurve(geo.prim(0));
	auto NN = NURBSCurve(geo.prim(1));

	BB.positions(BBP.data(), 0, BBP.size());
	NN.positions(NNP.data(), 0, NNP.size());

	REQUIRE(std::equal(BP.begin(), BP.end(), BBP.begin(), BBP.end()));
	REQUIRE(std::equal(NP.begin(), NP.end(), NNP.begin(), NNP.end()));
}

int main(int argc, char* const argv[]) {
	int result = Catch::Session().run(argc, argv);
	system("pause");
	return result;
}
