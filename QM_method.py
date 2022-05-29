#딕셔너리 원소의 기본값을 리스트로 만들기 위한 모듈
from collections import defaultdict
from itertools import product
import pandas

pi_list = [] #PI 리스트
check_set = set() #체크된 Minterm의 집합
optimal_pi_list = [] #채택된 PI들의 집합

#Minterm을 variable의 값으로 바꾸기 위한 함수
def convert_binary(variable_size:int, minterm_arr:list)->list:
    result = []
    for i in minterm_arr:
        binary = str(bin(i))[2:]
        binary = '0' * (variable_size - len(binary)) + binary
        result.append(binary)
    return result

#두 Minterm의 HammingDistance를 검사하고
#HammingDistance 관계이면 '-'로 치환할 인덱스를 반환
#False이면 -1을 반환

def isHamming(minterm1:str, minterm2:str)->int:
    count = 0
    index = 0
    for i in range(0, len(minterm1)):
        if minterm1[i] != minterm2[i]:
            count += 1
            index = i
    if (count == 1):
        return index
    else:
        return -1

#List를 받아 1의 갯수로 분류하는 딕셔너리 반환
def Classification_by_number_of_one(minterm_arr:list)->dict:
    list_of_dic = defaultdict(list)
    arr = minterm_arr
    for i in arr:
        number_of_1 = i.count('1')
        list_of_dic[number_of_1].append(i)
    return list_of_dic

#index값을 받아 Minterm의 index에 위치한 문자를 '-'로 치환하여 반환
def convert_minterm(minterm:str, index:int)->str:
    return minterm[:index] + '-' + minterm[index+1:]


#1의 갯수로 분류된 딕셔너리를 받아서 1의 갯수 차이가 한개씩인 Minterm들을 비교
#HammingDistance가 True, 즉 index값이 -1 이상이면 check_set에 원소들을 삽입
#두 Minterm에 생략할 수 있는 인덱스를 '-' 값으로 치환후 리스트에 삽입후 반환
#딕셔너리 안에서 check가 안된 Minterm들을 Pi_list에 삽입
def merge_hamming(dic:dict)->list:
    lst = []
    for dic_i in range(0, len(dic)-1):
        dic_keys = sorted(list(dic.keys()))
        index_1 = dic_keys[dic_i]; index_2 = dic_keys[dic_i+1]
        if index_2 - index_1 != 1:
            continue
        dic1 = dic[index_1]
        dic2 = dic[index_2]
        for i in dic1:
            for j in dic2:
                index = isHamming(i, j)
                if(index >= 0):
                    check_set.add(i)
                    check_set.add(j)
                    convert = convert_minterm(i, index) #i or j
                    lst.append(convert)
    find_pi(dic)

    return lst

#딕셔너리안에서 check가 안된 Minterm들을 Pi_list에 삽입
def find_pi(dic:dict):
    for arr_list in dic.values():
        for minterm in arr_list:
            if(minterm not in check_set):
                pi_list.append(minterm)

#Pi_list에 중복되는 Pi를 제거
def remove_duplication_and_sort(arr:list)->list:
    result = []
    for i in arr:
        if i not in result:
            result.append(i)
    result = sorted(result, key=lambda x: sort_key(x))
    return result

# '-'를 '2'로 취급하여 오름차순으로 정렬하기 위한 함수
def sort_key(pi):
    return pi.replace('-', '2')


#-------------------EPI--------------------

def isInclude(minterm, pi):
    size = len(pi)
    for i in range(size):
        if minterm[i] != pi[i] and pi[i] != '-':
            return False
    return True

def minterm_dic(pi_list, binary_minterm_list):
    match_minterm_pi = defaultdict(list)
    for pi in pi_list:
        for minterm in binary_minterm_list:
            if isInclude(minterm, pi):
                match_minterm_pi[minterm].append(pi)
    return match_minterm_pi

def pi_dic(pi_list, binary_minterm_list):
    match_minterm_pi = defaultdict(list)
    for pi in pi_list:
        for minterm in binary_minterm_list:
            if isInclude(minterm, pi):
                match_minterm_pi[pi].append(minterm)
    return match_minterm_pi

def find_epi(pi_list, binary_minterm_list):
    epi = []
    match_minterm_key = minterm_dic(pi_list, binary_minterm_list)
    for key in match_minterm_key.keys():
        if len(match_minterm_key[key]) == 1:
            epi += match_minterm_key[key]
    result = remove_duplication_and_sort(epi)
    return result

def cover_epi(epi_list, binary_minterm_list):
    remove_set = set()
    for epi in epi_list:
        pi_list.remove(epi)
        optimal_pi_list.append(epi)
        for minterm in binary_minterm_list:
            if isInclude(minterm, epi):
                remove_set.add(minterm)


    for minterm in remove_set:
        binary_minterm_list.remove(minterm)

#-------------------row_dominance--------------------------
def row_dominance(binary_minterm_list):
    pi_cover = pi_dic(pi_list, binary_minterm_list)
    row_dominance_set = set()
    same_set = set()
    seen = []
    for key_1, value_1 in pi_cover.items():
        for key_2, value_2 in pi_cover.items():
            set_1 = set(value_1)
            set_2 = set(value_2)
            if (key_1 != key_2) and (set_1.issubset(set_2)):
                row_dominance_set.add(key_1)
                if(set_1 == set_2) and (value_1 not in seen):
                    same_set.add(key_1)
                    seen.append(value_1)

    row_dominance_set -= same_set
    for pi in row_dominance_set:
        pi_list.remove(pi)

#-------------------column dominace------------------------
def column_dominance(binary_minterm_list):
    minterm_cover = minterm_dic(pi_list, binary_minterm_list)
    column_dominance_set = set()
    same_set = set()
    seen = []
    for key_1, value_1 in minterm_cover.items():
        for key_2, value_2 in minterm_cover.items():
            set_1 = set(value_1)
            set_2 = set(value_2)
            if (key_1 != key_2) and (set_1.issubset(set_2)):
                column_dominance_set.add(key_2)
                if(set_1 == set_2) and (value_1 not in seen):
                    same_set.add(key_2)
                    seen.append(value_2)

    column_dominance_set -= same_set
    for minterm in column_dominance_set:
        binary_minterm_list.remove(minterm)

    #column dominance 과정중 쓸모 없어진 pi 제거
    pi_cover = pi_dic(pi_list, binary_minterm_list)
    for pi in pi_list:
        if pi not in pi_cover.keys():
            pi_list.remove(pi)

#-----------------------petrick method--------------------------
def petrick_method(binary_minterm_list):
    minterm_cover = minterm_dic(pi_list, binary_minterm_list)
    temp = []
    petrick_result = []
    for value in minterm_cover.values():
        temp.append(value)

    product_list = list(map(lambda x: set(x), product(*temp)))
    optimal_length = len(min(product_list, key=lambda x: len(x)))
    for pro in product_list:
        if len(pro) == optimal_length:
            petrick_result.append(list(pro))

    for i in range(len(petrick_result)):
        petrick_result[i] += optimal_pi_list
        petrick_result[i] = remove_duplication_and_sort(petrick_result[i])

    return petrick_result


def rotation(binary_minterm_list):
    global optimal_pi_list
    while(1):
        flag = len(pi_list) + len(binary_minterm_list)

        epi_list = find_epi(pi_list, binary_minterm_list)
        print("\nCover EPI ----> ", epi_list)
        cover_epi(epi_list, binary_minterm_list)
        make_dataframe(pi_list, binary_minterm_list)

        print("#### OPTIMAL LIST : ", optimal_pi_list, " ###")

        if len(binary_minterm_list) == 0:
            break

        print("\nRow Dominance ")
        row_dominance(binary_minterm_list)
        make_dataframe(pi_list, binary_minterm_list)

        print("\nColumn Dominance")
        column_dominance(binary_minterm_list)
        make_dataframe(pi_list, binary_minterm_list)

        flag_2 = len(pi_list) + len(binary_minterm_list)

        if(flag == flag_2):
            break

    if pi_list:
        print("Run Petrick method")
        optimal_pi_list = petrick_method(binary_minterm_list)
    else:
        optimal_pi_list = [optimal_pi_list]

    return optimal_pi_list

def make_dataframe(pi_list, binary_minterm_list):
    match_minterm_key = minterm_dic(pi_list, binary_minterm_list)
    df = pandas.DataFrame(index=pi_list, columns=binary_minterm_list)
    pandas.set_option('mode.chained_assignment', None)
    for key in match_minterm_key.keys():
        values = match_minterm_key[key]
        column = key
        df[column][values] = 1
    df.dropna(how='all', inplace=True)
    df.dropna(how='all', axis=1, inplace=True)
    df.fillna('', inplace=True)
    if df.empty:
        print("EMPTY!!")
    else:
        print(df)

def convert_bin_to_SOP(variable_size, res):
    alpha_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    result_str = ''
    if(variable_size > len(alpha_list)-1):
        print("ERROR!!")
        return

    for pi in res:
        str = ''
        for index in range(len(pi)):
            if pi[index] != '-':
                str += alpha_list[index]
                if pi[index] == '0':
                    str += '\''
        str += '+'
        result_str += str

    return result_str[:-1]

def solution(minterm):
    global pi_list
    variable_size = minterm[0] #변수의 개수
    minterm_arr = minterm[1:] #Minterm의 리스트

    #Minterm을 변수의 형태로 변환 ex) 3 -> 0011
    binary_minterm_list = convert_binary(variable_size, minterm_arr)
    minterm_arr = binary_minterm_list

    #1의 갯수별로 Minterm을 분류
    arr_dic = Classification_by_number_of_one(minterm_arr)
    while(len(arr_dic) >= 1):#1의 갯수별로 분류된 딕셔너리 원소가 하나일 때 까지
        minterm_arr = merge_hamming(arr_dic) #Hamming Distance 원소들을 합침
        arr_dic = Classification_by_number_of_one(minterm_arr)#다시 1의 갯수로 분류


    pi_list = remove_duplication_and_sort(pi_list) #pi 리스트에서 중복 제거


    #pi_list = ['----', '0---', '01--']
    #binary_minterm_list = ["0110", "0111", "0101", "0100", "1111", "0011"]


    make_dataframe(pi_list, binary_minterm_list)
    rotation(binary_minterm_list)
    result_list = optimal_pi_list

    answer = []
    for res in result_list:
        answer.append(convert_bin_to_SOP(variable_size, res))

    print("result: ", answer)


#테스트 케이스
#minterm = [4, 1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 15]
#minterm = [4, 0, 4, 12, 8, 13, 15, 11, 10]
#minterm = [5, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 17, 20, 21, 23, 24, 26, 27]
#minterm = [5, 1, 2, 3, 4, 5, 6, 7, 20, 21, 23, 24, 26, 27 ,28, 29, 30]
#minterm = [3, 0, 1, 2, 5, 6, 7] #no epi
#minterm = [3, 0, 1, 2, 5, 6, 7]
#minterm = [4, 1, 2, 3, 5, 7, 8, 10, 13, 15]
#minterm = [4, 0, 1, 2 ,4, 5, 6, 9, 10, 11, 13, 14, 15]
#minterm = [3, 1, 3, 4, 6, 7]

#minterm = [6, 1, 2, 3, 5, 7, 8, 9, 10, 11, 12 ,13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 25, 26, 29, 30, 31, 32, 33, 34, 35, 36,
#           37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]

#pi_list = ['----','0---','01--','011-']; binary_minterm_list = ["0110, "0111"];

minterm = list(map(int, input().split()))
solution(minterm)