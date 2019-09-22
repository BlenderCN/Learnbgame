#pragma once

#include <assert.h>

#include <string>
#include <vector>
#include <memory>
#include <iostream>

///

#include <UT/UT_IStream.h>
#include <UT/UT_OStream.h>

#include <GA/GA_SaveOptions.h>
#include <GA/GA_LoadOptions.h>

#include <GU/GU_Detail.h>
#include <GU/GU_PrimitiveFactory.h>

#include <GEO/GEO_AttributeHandle.h>

#include <GEO/GEO_PrimNull.h>
#include <GEO/GEO_PrimPoly.h>
#include <GEO/GEO_PrimNURBCurve.h>
#include <GEO/GEO_PrimRBezCurve.h>
#include <GEO/GEO_PrimPart.h>

#include <GU/GU_PrimPoly.h>
#include <GU/GU_PrimNURBCurve.h>
#include <GU/GU_PrimRBezCurve.h>

///

namespace hio {

	using Size = int64_t;
	using Index = int64_t;
	static const Index INVALID_INDEX = -1;

	using PointIndex = Index;
	using VertexIndex = Index;
	using PrimitiveIndex = Index;

	class Point;
	class Vertex;
	class Primitive;
	class Geometry;

	class Polygon;
	class BezierCurve;
	class NURBSCurve;

	template <typename T, typename TT>
	struct Type2Enum {
		static constexpr TT value = 0;
	};

	using Vector2 = UT_Vector2T<float>;
	using Vector3 = UT_Vector3T<float>;
	using Vector4 = UT_Vector4T<float>;

	enum class AttribType
	{
		Point,
		Prim,
		Vertex,
		Global
	};

	enum class AttribData {
		Float,
		Int,
		String,
		Invalid
	};

	enum class TypeInfo {
		Point,
		Vector,
		Normal,
		Color,
		Matrix,
		Quaternion,
		TextureCoord,
		Value
	};

	enum class PrimitiveTypes {
		None = 0,
		Poly = 1 << 1,
		NURBSCurve = 1 << 2,
		BezierCurve = 1 << 3,
	};

	struct GA_PrimitiveTypeId_tag {};

	//////////////////////////////////////////////////////////////////////////

	inline int Enum2Enum(PrimitiveTypes v) {
		switch (v)
		{
			case hio::PrimitiveTypes::Poly: return GA_PRIMPOLY;
			case hio::PrimitiveTypes::NURBSCurve: return GA_PRIMNURBCURVE;
			case hio::PrimitiveTypes::BezierCurve: return GA_PRIMBEZCURVE;
			default: return GA_PRIMNONE;
		}
	}

	inline PrimitiveTypes Enum2Enum(int v, GA_PrimitiveTypeId_tag) {
		switch (v)
		{
			case GA_PRIMPOLY: return hio::PrimitiveTypes::Poly;
			case GA_PRIMNURBCURVE: return hio::PrimitiveTypes::NURBSCurve;
			case GA_PRIMBEZCURVE: return hio::PrimitiveTypes::BezierCurve;
			default: return hio::PrimitiveTypes::None;
		}
	}
	
	inline GA_StorageClass Enum2Enum(AttribData v) {
		switch (v)
		{
			case hio::AttribData::Float: return GA_STORECLASS_FLOAT;
			case hio::AttribData::Int: return GA_STORECLASS_INT;
			case hio::AttribData::String: return GA_STORECLASS_FLOAT;
			case hio::AttribData::Invalid: return GA_STORECLASS_INVALID;
		}
	}

	inline AttribData Enum2Enum(GA_StorageClass v) {
		switch (v)
		{
			case GA_STORECLASS_FLOAT: return hio::AttribData::Float;
			case GA_STORECLASS_INT: return hio::AttribData::Int;
			case GA_STORECLASS_STRING: return hio::AttribData::String;
			default: return hio::AttribData::Invalid;
		}
	}

	inline GA_AttributeOwner Enum2Enum(AttribType v) {
		switch (v)
		{
			case hio::AttribType::Point: return GA_ATTRIB_POINT;
			case hio::AttribType::Prim: return GA_ATTRIB_PRIMITIVE;
			case hio::AttribType::Vertex: return GA_ATTRIB_VERTEX;
			case hio::AttribType::Global: return GA_ATTRIB_GLOBAL;
			default: throw std::runtime_error("Invalid enum");
		}
	}

	inline AttribType Enum2Enum(GA_AttributeOwner v) {
		switch (v)
		{
			case GA_ATTRIB_POINT: return hio::AttribType::Point;
			case GA_ATTRIB_PRIMITIVE: return hio::AttribType::Prim;
			case GA_ATTRIB_VERTEX: return hio::AttribType::Vertex;
			case GA_ATTRIB_GLOBAL: return hio::AttribType::Global;
			default: throw std::runtime_error("Invalid enum");
		}
	}

	inline GA_TypeInfo Enum2Enum(TypeInfo v) {
		switch (v)
		{
			case hio::TypeInfo::Point: return GA_TYPE_POINT;
			case hio::TypeInfo::Vector: return GA_TYPE_VECTOR;
			case hio::TypeInfo::Normal: return GA_TYPE_NORMAL;
			case hio::TypeInfo::Color: return GA_TYPE_COLOR;
			case hio::TypeInfo::Matrix: return GA_TYPE_TRANSFORM;
			case hio::TypeInfo::Quaternion: return GA_TYPE_QUATERNION;
			case hio::TypeInfo::TextureCoord: return GA_TYPE_TEXTURE_COORD;
			case hio::TypeInfo::Value: return GA_TYPE_VOID;
			default: return GA_TYPE_VOID;
		}
	}

	inline TypeInfo Enum2Enum(GA_TypeInfo v) {
		switch (v)
		{
			case GA_TYPE_POINT: return hio::TypeInfo::Point;
			case GA_TYPE_VECTOR: return hio::TypeInfo::Vector;
			case GA_TYPE_NORMAL: return hio::TypeInfo::Normal;
			case GA_TYPE_COLOR: return hio::TypeInfo::Color;
			case GA_TYPE_TRANSFORM: return hio::TypeInfo::Matrix;
			case GA_TYPE_QUATERNION: return hio::TypeInfo::Quaternion;
			case GA_TYPE_TEXTURE_COORD: return hio::TypeInfo::TextureCoord;
			case GA_TYPE_VOID: return hio::TypeInfo::Value;
			default: return hio::TypeInfo::Value;
		}
	}

	template <> struct Type2Enum<float, AttribData> {
		static constexpr AttribData value = AttribData::Float;
	};

	template <> struct Type2Enum<int, AttribData> {
		static constexpr AttribData value = AttribData::Int;
	};

	template <> struct Type2Enum<std::string, AttribData> {
		static constexpr AttribData value = AttribData::String;
	};

	template <> struct Type2Enum<float, GA_StorageClass> {
		static constexpr GA_StorageClass value = GA_STORECLASS_FLOAT;
	};

	template <> struct Type2Enum<int, GA_StorageClass> {
		static constexpr GA_StorageClass value = GA_STORECLASS_INT;
	};

	template <> struct Type2Enum<std::string, GA_StorageClass> {
		static constexpr GA_StorageClass value = GA_STORECLASS_STRING;
	};

	//////////////////////////////////////////////////////////////////////////
	
	class Attrib
	{
	public:

		Attrib()
			: _attr(nullptr)
		{}

		Attrib(GA_Attribute* attr)
			: _attr(attr)
		{}

		Attrib(const GA_Attribute* attr)
			: _attr((GA_Attribute*)attr)
		{}

		Attrib& operator=(const Attrib& copy)
		{
			if (this == &copy) return *this;
			_attr = copy._attr;
			return *this;
		}

		std::string name() const { return _attr->getName().toStdString(); }
		AttribType type() const { return Enum2Enum(_attr->getOwner()); }
		AttribData dataType() const { return Enum2Enum(_attr->getStorageClass()); }
		TypeInfo typeInfo() const { return Enum2Enum(_attr->getTypeInfo()); }

		Size tupleSize() const { return _attr->getTupleSize(); }
		Size size() const {
			return _attr->getIndexMap().indexSize();
		}

		bool operator==(const Attrib& a) const { return _attr == a._attr; }
		bool operator!=(const Attrib& a) const { return _attr != a._attr; }
		operator bool() const { return (bool)_attr; }

		//////////////////////////////////////////////////////////////////////////

		template <typename T>
		void attribValue(void* out_data, Index offset = 0, Size size = -1) const
		{
			if (offset == 0 && size == -1)
				size = this->size() - offset;

			auto A = _attr;
			auto storage = A->getStorageClass();

			if (Type2Enum<T, GA_StorageClass>::value != storage)
				throw std::runtime_error("Storage type mismatch");

			if (offset < 0 || size < 0)
				throw std::runtime_error("Bound must be positive");

			if (offset > this->size() || offset + size > this->size())
				throw std::runtime_error("Array index out of bounds");

			const GA_AIFTuple* tuple = A->getAIFTuple();
			GA_Range range(A->getIndexMap(), GA_Offset(offset), GA_Offset(offset + size));

			int tuple_size = tuple->getTupleSize(A);
			int N = tuple_size * size;

			tuple->getRange(A, range, (T*)out_data, 0, tuple_size);
		}

		template <>
		void attribValue<std::string>(void* out_data, Index offset, Size size) const
		{
			if (offset == 0 && size == -1)
				size = this->size() - offset;

			auto A = _attr;
			auto storage = A->getStorageClass();

			if (Type2Enum<std::string, GA_StorageClass>::value != storage)
				throw std::runtime_error("Storage type mismatch");

			if (offset < 0 || size < 0)
				throw std::runtime_error("Bound must be positive");

			if (offset > this->size() || offset + size > this->size())
				throw std::runtime_error("Array index out of bounds");

			const GA_AIFStringTuple* tuple = A->getAIFStringTuple();

			std::string* out_str_data = (std::string*)out_data;

			for (int i = 0; i < size; i++)
			{
				out_str_data[i] = tuple->getString(A, i + offset);
			}
		}

		//////////////////////////////////////////////////////////////////////////

		template <typename T>
		void setAttribValue(const void* in_data, Index offset = 0, Size size = -1)
		{
			if (offset == 0 && size == -1)
				size = this->size() - offset;

			auto A = _attr;
			auto storage = A->getStorageClass();

			if (Type2Enum<T, GA_StorageClass>::value != storage)
				throw std::runtime_error("Storage type mismatch");

			if (offset < 0 || size < 0)
				throw std::runtime_error("Bound must be positive");

			if (offset > this->size() || offset + size > this->size())
				throw std::runtime_error("Array index out of bounds");

			const GA_AIFTuple* tuple = A->getAIFTuple();
			GA_Range range(A->getIndexMap(), GA_Offset(offset), GA_Offset(offset + size));

			int tuple_size = tuple->getTupleSize(A);
			int N = tuple_size * size;

			tuple->setRange(A, range, (const T*)in_data, 0, tuple_size);
		}

		template <>
		void setAttribValue<std::string>(const void* in_data, Index offset, Size size)
		{
			if (offset == 0 && size == -1)
				size = this->size() - offset;

			auto A = _attr;
			auto storage = A->getStorageClass();

			if (Type2Enum<std::string, GA_StorageClass>::value != storage)
				throw std::runtime_error("Storage type mismatch");

			if (offset < 0 || size < 0)
				throw std::runtime_error("Bound must be positive");

			if (offset > this->size() || offset + size > this->size())
				throw std::runtime_error("Array index out of bounds");

			const GA_AIFStringTuple* tuple = A->getAIFStringTuple();

			const std::string* in_str_data = (const std::string*)in_data;

			for (int i = 0; i < size; i++)
			{
				tuple->setString(A, i + offset, in_str_data[i].c_str(), 0);
			}
		}

		//////////////////////////////////////////////////////////////////////////

		GA_Attribute* attr() const { return _attr; }

	protected:

		GA_Attribute* _attr;
	};

	template <typename T>
	class Attrib_ : public Attrib
	{
	public:

		Attrib_()
			: Attrib()
		{}

		Attrib_(Attrib attr)
			: Attrib(attr.attr())
		{
			if (Type2Enum<T, AttribData>::value != attr.dataType())
			{
				throw std::runtime_error("Invalid cast");
			}
		}

		Attrib_(GA_Attribute* attr)
			: Attrib(attr)
		{}
	};

	///

	class Point
	{
	public:

		Point(Index index) : index(index) {}

		Index number() const { return index; }
		Vector3 position(const Geometry& geo) const;
		void setPosition(Geometry& geo, const Vector3& P);

		template <typename T>
		void attribValue(Attrib attr, void* out_data) const
		{
			attr.attribValue<T>(out_data, number(), 1);
		}

		template <typename T>
		void setAttribValue(Attrib attr, void* in_data) const
		{
			attr.setAttribValue<T>(in_data, number(), 1);
		}

	public:

		operator Index() const { return number(); }

	private:

		const Index index;
	};

	class Vertex
	{
	public:

		Vertex(Index index) : index(index) {}

		Index number() const { return index; }

		template <typename T>
		void attribValue(Attrib attr, void* out_data) const
		{
			attr.attribValue<T>(out_data, number(), 1);
		}

		template <typename T>
		void setAttribValue(Attrib attr, void* in_data) const
		{
			attr.setAttribValue<T>(in_data, number(), 1);
		}

	public:

		operator Index() const { return number(); }

	private:

		Index index;
	};

	class Primitive
	{
	public:

		Primitive(GEO_Primitive* prim) : _prim(prim) {}
		Primitive(const GEO_Primitive* prim) : _prim((GEO_Primitive*)prim) {}

		Primitive(const Primitive& copy) : _prim(copy._prim) {}
		Primitive& operator=(const Primitive& copy)
		{
			_prim = copy._prim;
			return *this;
		}
		virtual ~Primitive() = default;

		Index number() const { return _prim->getMapIndex(); }

		template <typename T>
		void attribValue(Attrib attr, void* out_data) const
		{
			attr.attribValue<T>(out_data, number(), 1);
		}

		template <typename T>
		void setAttribValue(Attrib attr, void* in_data) const
		{
			attr.setAttribValue<T>(in_data, number(), 1);
		}

		//////////////////////////////////////////////////////////////////////////

		void setPositions(const Vector3* data, Index offset = 0, Size size = -1);
		void positions(Vector3* out_data, Index offset, Size size);

		//////////////////////////////////////////////////////////////////////////

		std::vector<Index> vertices() const {
			std::vector<Index> arr(_prim->getVertexCount());
			for (int i = 0; i < arr.size(); i++)
				arr[i] = _prim->getPointIndex(i);
			return arr;
		}

		Index vertexStartIndex() const {
			return _prim->getVertexIndex(0);
		}

		Size vertexCount() const {
			return _prim->getVertexCount();
		}

		Vertex vertex(Index index);

	public:

		operator Index() const { return _prim->getMapIndex(); }

		GEO_Primitive* prim() { return _prim; }
		const GEO_Primitive* prim() const { return _prim; }

		bool valid() const { return _prim != nullptr; }

	protected:

		GEO_Primitive* _prim;
	};

	class Polygon : public Primitive
	{
	public:

		static constexpr int prim_typeid = GA_PRIMPOLY;

		Polygon(GEO_Primitive* prim);
		Polygon(const Primitive& cast);

		Polygon(const Polygon& copy)
			: Primitive(copy.prim())
		{}

		Polygon& operator=(const Polygon& copy)
		{
			Primitive::operator=(copy);
			return *this;
		}

		Vertex addVertex(Point point);

		bool isClosed() const { return poly()->isClosed(); }
		void setIsClosed(bool isclosed) { poly()->setClosed(isclosed); }

	private:

		GEO_PrimPoly* poly() {
			return (GEO_PrimPoly*)_prim;
		}

		const GEO_PrimPoly* poly() const {
			return (const GEO_PrimPoly*)_prim;
		}
	};

	class BezierCurve : public Primitive
	{
	public:

		static constexpr int prim_typeid = GA_PRIMBEZCURVE;

		BezierCurve(GEO_Primitive* prim);
		BezierCurve(const Primitive& cast);

		BezierCurve(const BezierCurve& copy)
			: BezierCurve(copy.prim())
		{}

		BezierCurve& operator=(const BezierCurve& copy)
		{
			Primitive::operator=(copy);
			return *this;
		}

		Vertex addVertex(Point point);

		bool isClosed() const { return curve()->isClosed(); }
		void setIsClosed(bool isclosed) { curve()->setClosed(isclosed); }

	private:

		GEO_PrimRBezCurve* curve() {
			return (GEO_PrimRBezCurve*)_prim;
		}

		const GEO_PrimRBezCurve* curve() const {
			return (const GEO_PrimRBezCurve*)_prim;
		}
	};

	class NURBSCurve : public Primitive
	{
	public:

		static constexpr int prim_typeid = GA_PRIMNURBCURVE;

		NURBSCurve(GEO_Primitive* prim);
		NURBSCurve(const Primitive& cast);

		NURBSCurve(const NURBSCurve& copy)
			: NURBSCurve(copy.prim())
		{}

		NURBSCurve& operator=(const NURBSCurve& copy)
		{
			Primitive::operator=(copy);
			return *this;
		}

		Vertex addVertex(Point point);

		bool isClosed() const { return curve()->isClosed(); }
		void setIsClosed(bool isclosed) { curve()->setClosed(isclosed); }

	private:

		GEO_PrimNURBCurve* curve() {
			return (GEO_PrimNURBCurve*)_prim;
		}

		const GEO_PrimNURBCurve* curve() const {
			return (const GEO_PrimNURBCurve*)_prim;
		}
	};

	//////////////////////////////////////////////////////////////////////////

	class Geometry
	{
	public:

		Geometry();

		void clear();

		Size getNumPoints() const;
		Size getNumVertices() const;
		Size getNumPrimitives() const;

		Point createPoint();
		std::vector<Point> createPoints(Size size);
		std::vector<Point> createPoints(Size size, const Vector3* data);

		Point point(Index index) const;
		std::vector<Point> points() const;

		Primitive prim(Index index) const;
		std::vector<Primitive> prims() const;

		Polygon createPolygon(Size num_vertices = 0, bool is_closed = true);

		std::vector<Polygon> createPolygons(Size position_size, const Vector3* positions,
			Size vertex_counts_size, const Size* vertex_counts,
			bool closed = true);
		std::vector<Polygon> createPolygons(Size position_size, const Vector3* positions,
			Size vertices_size, const Index* vertices,
			Size vertex_counts_size, const Size* vertex_counts,
			bool closed = true);

		BezierCurve createBezierCurve(Size num_vertices, bool is_closed = false, int order = 4);
		NURBSCurve createNURBSCurve(Size num_vertices, bool is_closed = false, int order = 4, int _interp_ends = -1);

		void deletePrims(const std::vector<Primitive>& prims, bool keep_points = false);

		std::vector<Attrib> pointAttribs() const;
		std::vector<Attrib> primAttribs() const;
		std::vector<Attrib> vertexAttribs() const;
		std::vector<Attrib> globalAttribs() const;

		template <typename T>
		Attrib_<T> addAttrib(AttribType type, const std::string& name, const std::vector<T>& default_value, TypeInfo typeinfo);

		Attrib findPointAttrib(const std::string& name) const;
		Attrib findPrimAttrib(const std::string& name) const;
		Attrib findVertexAttrib(const std::string& name) const;
		Attrib findGlobalAttrib(const std::string& name) const;

		template <typename T>
		std::vector<T> attribValue(const std::string& name);

		template <typename T>
		std::vector<T> attribValue(Attrib attr);

		///

		bool load(const std::string& path);
		bool save(const std::string& path);

		GU_Detail& geo() { return _geo; }
		const GU_Detail& geo() const { return _geo; }

	private:

		GU_Detail _geo;
	};

	/////////////////////////////////////////////////////

	template <typename T>
	std::vector<T>
		hio::Geometry::attribValue(const std::string& name)
	{
		return attribValue<T>(findGlobalAttrib(name));
	}

	template <typename T>
	std::vector<T>
		hio::Geometry::attribValue(Attrib attr)
	{
		std::vector<T> arr;
		Attrib_<T> a = attr;

		a.attribValue<T>(_geo.getGlobalRange());

		return arr;
	}

	//

	template <typename T>
	inline Attrib_<T>
		hio::Geometry::addAttrib(AttribType type,
			const std::string& name,
			const std::vector<T>& default_value,
			TypeInfo typeinfo)
	{}

	template <>
	inline Attrib_<float>
		hio::Geometry::addAttrib(AttribType type,
			const std::string& name,
			const std::vector<float>& default_value,
			TypeInfo typeinfo)
	{
		GA_AttributeOwner t = Enum2Enum(type);
		GA_Attribute* attr = _geo.addFloatTuple(t, name.c_str(),
			default_value.size(),
			GA_Defaults(default_value.data(), default_value.size()));
		attr->setTypeInfo(Enum2Enum(typeinfo));
		return Attrib_<float>(attr);
	}

	template <>
	inline Attrib_<int>
		hio::Geometry::addAttrib(AttribType type,
			const std::string& name,
			const std::vector<int>& default_value,
			TypeInfo typeinfo)
	{
		GA_AttributeOwner t = Enum2Enum(type);
		GA_Attribute* attr = _geo.addIntTuple(t, name.c_str(),
			default_value.size(),
			GA_Defaults(default_value.data(), default_value.size()));
		attr->setTypeInfo(Enum2Enum(typeinfo));
		return Attrib_<int>(attr);
	}

	template <>
	inline Attrib_<std::string>
		hio::Geometry::addAttrib(AttribType type,
			const std::string& name,
			const std::vector<std::string>& default_value,
			TypeInfo typeinfo)
	{

		GA_AttributeOwner t = Enum2Enum(type);
		GA_Attribute* attr = _geo.addStringTuple(t, name.c_str(),
			default_value.size());
		attr->setTypeInfo(Enum2Enum(typeinfo));
		return Attrib_<std::string>(attr);
	}

}

