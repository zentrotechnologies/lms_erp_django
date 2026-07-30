from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from .models import *
from .serializers import *
from lms.settings import *
from django.contrib.auth.hashers import make_password,check_password
from adminauth.jwt import *
from adminauth.models import *
from master.serializers import *
from master.models import *
from adminauth.serializers import *
from helpers.validations import *
from rest_framework import permissions
from course.models import *
# Create your views here.
from django.db.models import Q
from datetime import date



class GetEligibileCountryPaginationList(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPagination

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        
        msg=''
        eligible_country_obj = Country.objects.filter(isActive=True,is_eligibile=True).order_by('name')
        if eligible_country_obj.exists():
            paginate_object = self.paginate_queryset(eligible_country_obj)
            
            serializer =  CountrySerializer(paginate_object,many=True)
            country_list=serializer.data

            all_department_objs=Department.objects.filter(isActive=True)
            departments_serializer=DepartmentSerializer(all_department_objs,many=True)
            
            all_rank_objs=Rank.objects.filter(isActive=True)
            ranks_serializer=RankSerializer(all_rank_objs,many=True)
            
            all_qualifications_objs=EducationalQualifications.objects.filter(isActive=True)
            qualifications_serializer=EducationalQualificationsSerializer(all_qualifications_objs,many=True)
            
            all_documents_objs=Documents.objects.filter(isActive=True,role=6,status=True)
            documents_serializer=DocumentsSerializer(all_documents_objs,many=True)
            
            for country in country_list:
                country['rules']=[]
                country_rules_objs=GeneralEligibilityRules.objects.filter(country_id=country['id'],isActive=True).order_by('createdAt')
                if country_rules_objs.exists():
                    rules_serializer=GeneralEligibilityRulesSerializer(country_rules_objs,many=True)
                    country['rules']=rules_serializer.data
                    
                    general_eligibility_rule_ids=list(GeneralEligibilityRules.objects.filter(country_id=country['id'],isActive=True).order_by('id').values_list('id',flat=True))

                    for rule in country['rules']:
                        rule['Departments']=departments_serializer.data



                        rule['departments_ids']=list(GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id=rule['id'],isActive=True).values_list('departments',flat=True))

                        first_combination_obj=GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id=rule['id'],isActive=True).first()
                        if first_combination_obj is not None:
                            
                            rule['minimum_age']=first_combination_obj.minimum_age
                        else:
                            rule['minimum_age']=""

                        
                        
                        exist_rank_ids=list(GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id__in=general_eligibility_rule_ids,isActive=True).values_list('ranks',flat=True))
                        

                        exclude_already_exists_rank=all_rank_objs.filter(department_name__in=rule['departments_ids']).exclude(id__in=exist_rank_ids)
                        r_ranks_serializer= RankSerializer(exclude_already_exists_rank,many=True)
                        rule['Ranks']=r_ranks_serializer.data


                        rule_ranks=all_rank_objs.filter(id__in=list(GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id=rule['id'],isActive=True).values_list('ranks',flat=True)))
                        rule_ranks_serializer= RankSerializer(rule_ranks,many=True)
                        rule['ranks_ids']=rule_ranks_serializer.data

                        rule['Qualifications']=qualifications_serializer.data
                        rule['qualifications_ids']=list(GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=rule['id'],isActive=True).values_list('educational_qualification_id',flat=True))


                        rule['MandatoryDocuments']=documents_serializer.data
                        rule['documents_ids']=list(GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=rule['id'],isActive=True).values_list('document_id',flat=True))
               
            if encryped_header == "1" :
                paigna=self.get_paginated_response(country_list)
                data_to_serialize = convert_decimals_to_float(paigna)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                paigna=self.get_paginated_response(country_list)
                return Response(paigna,status=200)
                    
        else:
            response_={
                        "n": 0,
                        "msg": "No country is eligibile",
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)






class GetCountryRuleFormDetails(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        
        country_id=request_data.get('country_id')
        msg=''
        eligible_country_obj = Country.objects.filter(id=country_id,isActive=True,is_eligibile=True).first()
        if eligible_country_obj is not None:
            serializer =  CountrySerializer(eligible_country_obj)
            country_data=serializer.data
            
            all_department_objs=Department.objects.filter(isActive=True)
            departments_serializer=DepartmentSerializer(all_department_objs,many=True)
            
            
            all_rank_objs=Rank.objects.filter(isActive=True)
            
            general_eligibility_rule_ids=list(GeneralEligibilityRules.objects.filter(country_id=country_id,isActive=True).order_by('id').values_list('id',flat=True))
                        
            exist_rank_ids=list(GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id__in=general_eligibility_rule_ids,isActive=True).values_list('ranks',flat=True))
                        

            all_rank_objs=all_rank_objs.exclude(id__in=exist_rank_ids)
            ranks_serializer=RankSerializer(all_rank_objs,many=True)








            all_qualifications_objs=EducationalQualifications.objects.filter(isActive=True)
            qualifications_serializer=EducationalQualificationsSerializer(all_qualifications_objs,many=True)
            
            all_documents_objs=Documents.objects.filter(isActive=True,role=6,status=True)
            documents_serializer=DocumentsSerializer(all_documents_objs,many=True)
            
  

            country_data['Departments']=departments_serializer.data
            country_data['Ranks']=ranks_serializer.data
            country_data['Qualifications']=qualifications_serializer.data
            country_data['MandatoryDocuments']=documents_serializer.data
               


            response_={
                        "n": 1,
                        "msg": 'Country rules details found successfully',
                        "data":country_data  ,                      
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)
                    
        else:
            response_={
                        "n": 0,
                        "msg": "No country is eligibile",
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class DeleteGeneralEligibilityRules(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        

        country_id=request_data.get('country_id')
        rule_id=request_data.get('rule_id')
        msg=''
        country_general_eligibility_obj = GeneralEligibilityRules.objects.filter(id=rule_id,isActive=True).first()
        if country_general_eligibility_obj is not None:
            data={}
            data['isActive']=False
            serializer =  GeneralEligibilityRulesSerializer(country_general_eligibility_obj,data=data)
            if serializer.is_valid():
                serializer.save()
                response_={
                            "n": 1,
                            "msg": 'Rules deleted successfully',
                            "data":serializer.data  ,                      
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)
            else:
                response_={
                            "n": 0,
                            "msg": "serializer.errors",
                            "data":[]                     
                        }
                if encryped_header == "1" :
                    data_to_serialize = convert_decimals_to_float(response_)
                    encdata = encrypt_data(json.dumps(data_to_serialize))
                    return Response(encdata,status=200)
                else:
                    return Response(response_,status=200)

        else:
            response_={
                        "n": 0,
                        "msg": "Country General Eligibility rule not found",
                        "data":[]                     
                    }
            if encryped_header == "1" :
                data_to_serialize = convert_decimals_to_float(response_)
                encdata = encrypt_data(json.dumps(data_to_serialize))
                return Response(encdata,status=200)
            else:
                return Response(response_,status=200)


class SaveCountryRuleDetails(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        

        country_id=request_data.get('country_id')
        all_rules_list=request_data.get('all_rules_list')
        for rule in all_rules_list:
            
            if rule['saved'] == True:
                country_general_eligibility_obj = GeneralEligibilityRules.objects.filter(country_id=country_id,isActive=True,id=rule['id']).first()


                if country_general_eligibility_obj is not None:

                    GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id=country_general_eligibility_obj.id).update(isActive=False)
                    
                    Department_Rank_Combinations_Array=[]
                    for rank in rule['rank_ids']:
                        rank_obj=Rank.objects.filter(id=rank,isActive=True).first()
                        if rank_obj is not None:
                            department_id=str(rank_obj.department_name)
                            if department_id in rule['department_ids']:
                               
                                Department_Rank_Combinations_Array.append({
                                    'general_eligibility_rule_id':country_general_eligibility_obj.id,
                                    'departments':department_id,
                                    'ranks':rank,
                                    'minimum_age':rule['minimum_age'],
                                })
                                already_exist_com_obj=GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id=country_general_eligibility_obj.id,departments=department_id,ranks=rank).first()
                                if already_exist_com_obj is None:
                                    GeneralEligibilityDepartmentRankCombinations.objects.create(general_eligibility_rule_id=country_general_eligibility_obj.id,departments=department_id,ranks=rank,minimum_age=rule['minimum_age'],isActive=True)
                                else:
                                    GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id=country_general_eligibility_obj.id,departments=department_id,ranks=rank,).update(isActive=True,minimum_age=rule['minimum_age'],)
                                




                    GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=country_general_eligibility_obj.id).update(isActive=False)
                    
                    for qualification in rule['qualifications_ids']:
                        already_exist_quali_obj=GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=country_general_eligibility_obj.id,educational_qualification_id=qualification).first()
                        if already_exist_quali_obj is None:
                            GeneralEligibilityEducationalQualifications.objects.create(general_eligibility_rule_id=country_general_eligibility_obj.id,educational_qualification_id=qualification,isActive=True)
                        else:
                            GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=country_general_eligibility_obj.id,educational_qualification_id=qualification,).update(isActive=True)



                    GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=country_general_eligibility_obj.id).update(isActive=False)
                    
                    for document in rule['mandatory_documents_ids']:
                        already_exist_doc_obj=GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=country_general_eligibility_obj.id,document_id=document).first()
                        if already_exist_doc_obj is None:
                            GeneralEligibilityMandatoryDocuments.objects.create(general_eligibility_rule_id=country_general_eligibility_obj.id,document_id=document,isActive=True)
                        else:
                            GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=country_general_eligibility_obj.id,document_id=document,).update(isActive=True)
            else:
                country_obj=Country.objects.filter(id=country_id,isActive=True,is_eligibile=True).first()
                if country_obj is not None:
                    data={}
                    data['country_id']=country_obj.id
                    data['country_name']=country_obj.name
                    data['rule_no']=GeneralEligibilityRules.objects.filter(country_id=country_obj.id).count()+1
                    

                    serializer=GeneralEligibilityRulesSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()

                        
                

                        GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id=serializer.data['id']).update(isActive=False)
                    
                        Department_Rank_Combinations_Array=[]
                        for rank in rule['rank_ids']:
                            rank_obj=Rank.objects.filter(id=rank,isActive=True).first()
                            if rank_obj is not None:
                                department_id=str(rank_obj.department_name)
                                if department_id in rule['department_ids']:
                                    Department_Rank_Combinations_Array.append({
                                        'general_eligibility_rule_id':serializer.data['id'],
                                        'departments':department_id,
                                        'ranks':rank,
                                        'minimum_age':rule['minimum_age'],
                                    })
                                    already_exist_com_obj=GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id=serializer.data['id'],departments=department_id,ranks=rank).first()
                                    if already_exist_com_obj is None:
                                        GeneralEligibilityDepartmentRankCombinations.objects.create(general_eligibility_rule_id=serializer.data['id'],departments=department_id,ranks=rank,minimum_age=rule['minimum_age'],isActive=True)
                                    else:
                                        GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id=serializer.data['id'],departments=department_id,ranks=rank,).update(isActive=True,minimum_age=rule['minimum_age'],)
                                    




                        GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=serializer.data['id']).update(isActive=False)
                        
                        for qualification in rule['qualifications_ids']:
                            already_exist_quali_obj=GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=serializer.data['id'],educational_qualification_id=qualification).first()
                            if already_exist_quali_obj is None:
                                GeneralEligibilityEducationalQualifications.objects.create(general_eligibility_rule_id=serializer.data['id'],educational_qualification_id=qualification,isActive=True)
                            else:
                                GeneralEligibilityEducationalQualifications.objects.filter(general_eligibility_rule_id=serializer.data['id'],educational_qualification_id=qualification,).update(isActive=True)



                        GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=serializer.data['id']).update(isActive=False)
                        
                        for document in rule['mandatory_documents_ids']:
                            already_exist_doc_obj=GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=serializer.data['id'],document_id=document).first()
                            if already_exist_doc_obj is None:
                                GeneralEligibilityMandatoryDocuments.objects.create(general_eligibility_rule_id=serializer.data['id'],document_id=document,isActive=True)
                            else:
                                GeneralEligibilityMandatoryDocuments.objects.filter(general_eligibility_rule_id=serializer.data['id'],document_id=document,).update(isActive=True)
                    else:
                        print("error",serializer.errors)


        response_={
                    "n": 1,
                    "msg": 'Rules details saved successfully',
                    "data":[]  ,                      
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
          
        
class GetCountryExistingRuleIds(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        

        country_id=request_data.get('country_id')
        country_general_eligibility_ids = list(GeneralEligibilityRules.objects.filter(country_id=country_id,isActive=True).values_list('id',flat=True))
        response_={
                    "n": 1,
                    "msg": 'Rules ids found successfully',
                    "data":country_general_eligibility_ids  ,                      
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
           

class GetUnmappedRanks(GenericAPIView):
    authentication_classes=[UserAdminJWTAuthentication]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        encryped_header = ""
        if 'encrypted' in request.headers.keys():
            encryped_header = request.headers.get('encrypted')
        
        request_data, error_response = handle_request_body(request)
        if error_response:
            return error_response
        

        country_id=request_data.get('country_id')
        departments=request_data.get('department_ids')
        country_general_eligibility_ids = list(GeneralEligibilityRules.objects.filter(country_id=country_id,isActive=True).values_list('id',flat=True))
        
        exist_rank_ids_obj=GeneralEligibilityDepartmentRankCombinations.objects.filter(general_eligibility_rule_id__in=country_general_eligibility_ids,isActive=True)

        general_eligibility_rule_id=request_data.get('general_eligibility_rule_id')

        if general_eligibility_rule_id is not None and general_eligibility_rule_id !='':
            exist_rank_ids=list(exist_rank_ids_obj.exclude(general_eligibility_rule_id=general_eligibility_rule_id).values_list('ranks',flat=True))
        else:
            exist_rank_ids=list(exist_rank_ids_obj.values_list('ranks',flat=True))



                        
        all_rank_objs=Rank.objects.filter(isActive=True,status=True,department_name__in=departments)
        all_rank_objs=all_rank_objs.exclude(id__in=exist_rank_ids)
        ranks_serializer=RankSerializer(all_rank_objs,many=True)










        response_={
                    "n": 1,
                    "msg": 'Ranks   found successfully',
                    "data":ranks_serializer.data  ,                      
                }
        if encryped_header == "1" :
            data_to_serialize = convert_decimals_to_float(response_)
            encdata = encrypt_data(json.dumps(data_to_serialize))
            return Response(encdata,status=200)
        else:
            return Response(response_,status=200)
           





