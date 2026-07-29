#from django.shortcuts import render #djangoフレームワークのrender関数を呼び出す(非同期処理のため使わない)
from django.http import JsonResponse #Json形式で返せるためのおまじない

# Create your views here.

def convert_api(request): #/api/convertにアクセスが来たときに呼び出す
    return JsonResponse({"message":"convert api ok"}) #convert api okというメッセージをJson形式で返す(暫定)

def result_detail_api(request,pk): #/api/results/数字/にアクセスが来たとき
    return JsonResponse({"result_id":pk}) #pkに数字を入れてJson形式で返す