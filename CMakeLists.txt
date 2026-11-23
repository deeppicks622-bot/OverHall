cmake_minimum_required(VERSION 3.20)
project(OverHall VERSION 0.1.0 LANGUAGES CXX)

add_executable(overhall src/main.cpp)
target_compile_features(overhall PRIVATE cxx_std_20)

if(MSVC)
    target_compile_options(overhall PRIVATE /W4 /permissive-)
else()
    target_compile_options(overhall PRIVATE -Wall -Wextra -Wpedantic)
endif()
