// VECTOR3.h
#ifndef VECTOR3_HPP
#define VECTOR3_HPP

#include <cmath> // for std::sqrt

template <typename T>
class vec2 {
public:
    T x, y;
    
    // 构造函数
    vec2(T _x = 0, T _y = 0) : x(_x), y(_y) {}
    
    // 向量加法
    vec2<T> operator+(const vec2<T>& other) const {
        return vec2<T>(x + other.x, y + other.y);
    }
    
    // 向量减法
    vec2<T> operator-(const vec2<T>& other) const {
        return vec2<T>(x - other.x, y - other.y);
    }
    
    // 标量乘法
    vec2<T> operator*(T scalar) const {
        return vec2<T>(x * scalar, y * scalar);
    }
    
    // 点积
    T dot(const vec2<T>& other) const {
        return x * other.x + y * other.y;
    }
    
    // 向量长度
    T length() const {
        return std::sqrt(x * x + y * y);
    }
    
    // 单位向量
    vec2<T> normalized() const {
        T len = length();
        if (len > 0) {
            return vec2<T>(x / len, y / len);
        }
        return vec2<T>();
    }
    
    // 判断是否为零向量
    bool is_zero() const {
        return (x == 0 && y == 0);
    }
};

template <typename T>
class vec3 : public vec2<T> {
public:
    T z;
    
    // 构造函数
    vec3(T _x = 0, T _y = 0, T _z = 0) : vec2<T>(_x, _y), z(_z) {}
    // 从 vec2 构造，z 默认为 0
    vec3(const vec2<T>& v2){
        this->x = v2.x;
        this->y = v2.y;
        z = 0;
    }
    // 向量加法
    vec3<T> operator+(const vec3<T>& other) const {
        return vec3<T>(this->x + other.x, this->y + other.y, z + other.z);
    }
    
    // 向量减法
    vec3<T> operator-(const vec3<T>& other) const {
        return vec3<T>(this->x - other.x, this->y - other.y, z - other.z);
    }
    
    // 标量乘法
    vec3<T> operator*(T scalar) const {
        return vec3<T>(this->x * scalar, this->y * scalar, z * scalar);
    }
    
    // 叉积
    vec3<T> cross(const vec3<T>& other) const {
        return vec3<T>(
            this->y * other.z - z * other.y,
            z * other.x - this->x * other.z, 
            this->x * other.y - this->y * other.x
        );
    }
    
    // 点积
    T dot(const vec3<T>& other) const {
        return vec2<T>::dot(other) + z * other.z;
    }
    
    // 向量长度
    T length() const {
        return std::sqrt(this->x * this->x + this->y * this->y + z * z);
    }
    
    // 单位向量
    vec3<T> normalized() const {
        T len = length();
        if (len > 0) {
            return vec3<T>(this->x / len, this->y / len, z / len);
        }
        return vec3<T>();
    }
    
    // 判断是否为零向量
    bool is_zero() const {
        return vec2<T>::is_zero() && (z == 0);
    }
};
#endif // VECTOR3_HPP