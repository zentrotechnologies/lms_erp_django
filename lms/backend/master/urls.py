from . import views
from django.urls import include, path

urlpatterns = [
    path('add-category',views.AddCategory.as_view(), name='post'),
    path('category-list',views.CategoryList.as_view(), name='post'),
    path('subcat-category-list',views.SubcatCategoryList.as_view(), name='post'),

    path('update-category',views.UpdateCategory.as_view(), name='post'),
    path('delete-category',views.DeleteCategory.as_view(), name='post'),
    path('change-category-status',views.ChangeCategoryStatus.as_view(), name='post'),

    # 
    path('add-sub-category',views.AddSub_Category.as_view(), name='post'),
    path('sub-category-list',views.Sub_CategoryList.as_view(), name='post'),
    path('update-sub-category',views.UpdateSub_Category.as_view(), name='post'),
    path('delete-sub-category',views.DeleteSub_Category.as_view(), name='post'),
    path('change-sub-category-status',views.ChangeSubCategoryStatus.as_view(), name='post'),

    # 
    path('add-department',views.AddDepartment.as_view(), name='post'),
    path('department-list',views.DepartmentList.as_view(), name='post'),
    path('update-department',views.UpdateDepartment.as_view(), name='post'),
    path('delete-department',views.DeleteDepartment.as_view(), name='post'),
    path('change-department-status',views.ChangeDepartmentStatus.as_view(), name='post'),

    # 
    path('add-rank',views.AddRank.as_view(), name='post'),
    path('rank-list',views.RankList.as_view(), name='post'),
    path('update-rank',views.UpdateRank.as_view(), name='post'),
    path('delete-rank',views.DeleteRank.as_view(), name='post'),
    path('change-rank-status',views.ChangeRankStatus.as_view(), name='post'),
    path('get-department-ranks',views.GetDepartmentRanks.as_view(), name='post'),


    # 
    path('add-documents',views.AddDocuments.as_view(), name='post'),
    path('documents-list',views.DocumentsList.as_view(), name='post'),
    path('update-documents',views.UpdateDocuments.as_view(), name='post'),
    path('delete-documents',views.DeleteDocuments.as_view(), name='post'),
    path('change-document-status',views.ChangeDocumentStatus.as_view(), name='post'),
    # 
    path('add-languages',views.AddLanguages.as_view(), name='post'),
    path('languages-list',views.LanguagesList.as_view(), name='post'),
    path('update-languages',views.UpdateLanguages.as_view(), name='post'),
    path('delete-languages',views.DeleteLanguages.as_view(), name='post'),
    # 
    path('add-specialization',views.AddSpecialization.as_view(), name='post'),
    path('specialization-list',views.SpecializationList.as_view(), name='post'),
    path('update-specialization',views.UpdateSpecialization.as_view(), name='post'),
    path('delete-specialization',views.DeleteSpecialization.as_view(), name='post'),
    
    #branch
    path('add-branch',views.AddBranch.as_view(), name='post'),
    path('update-branch',views.UpdateBranch.as_view(), name='post'),
    path('branch-detail',views.BranchDetails.as_view(), name='post'),
    path('branch-documents',views.UploadBranchDocumentFormData.as_view(), name='post'),
    path('branch-list',views.BranchList.as_view(), name='post'),


    #s3-upload
    path('save-s3uploads',views.SaveS3Uploads.as_view(), name='post'),
    path('s3uploads-list',views.S3UploadsList.as_view(), name='get'),
    path('delete-s3file',views.DeleteS3File.as_view(), name='post'),


    #enquiries
    path('add-enquiry',views.AddEnquiry.as_view(), name='post'),
    path('enquiry-list',views.EnquiryList.as_view(), name='post'),
    # path('get-enquiry',views.GetEnquiry.as_view(), name='post'),

    #vessel
    path('vessel-list',views.VesselList.as_view(), name='post'),
    path('add-vessel',views.AddVessel.as_view(), name='post'),
    path('add-vessel-details',views.AddVesselDetails.as_view(), name='post'),
    path('get-vessel-details',views.GetVesselDetails.as_view(), name='post'),
    path('update-vessel',views.UpdateVessel.as_view(), name='post'),
    path('delete-vessel',views.DeleteVessel.as_view(), name='post'),
    path('change-vessel-status',views.ChangeVesselStatus.as_view(), name='post'),

    path('get-documents',views.GetDocuments.as_view(), name='post'),
    path('get-qualifications',views.GetQualifications.as_view(), name='post'),

   
    #country
    path('add-country',views.AddCountry.as_view(), name='post'),
    path('country-list',views.CountryList.as_view(), name='post'),
    path('update-country',views.UpdateCountry.as_view(), name='post'),
    path('delete-country',views.DeleteCountry.as_view(), name='post'),
    path('change-country-status',views.ChangeCountryStatus.as_view(), name='post'),
    path('get-state-country',views.GetStateCountry.as_view(), name='post'),



    path('ticket-category-list',views.TicketCategoryList.as_view(), name='post'),
    path('add-ticket-category',views.AddTicketCategory.as_view(), name='post'),
    path('update-ticket-category',views.UpdateTicketCategory.as_view(), name='post'),
    path('delete-ticket-category',views.DeleteTicketCategory.as_view(), name='post'),
    path('change-ticket-category-status',views.ChangeTicketCategoryStatus.as_view(), name='post'),


    path('add-feedback-sub-category',views.AddFeedbackSubCategory.as_view(), name='post'),
    path('feedback-sub-category-list',views.FeedbackSubCategoryList.as_view(), name='post'),
    path('update-feedback-sub-category',views.UpdateFeedbackSubCategory.as_view(), name='post'),
    path('delete-feedback-sub-category',views.DeleteFeedbackSubCategory.as_view(), name='post'),
    path('change-feedback-sub-category-status',views.ChangeFeedbackSubCategoryStatus.as_view(), name='post'),





    path('add-educational-qualification',views.AddEducationalQualification.as_view(), name='post'),
    path('educational-qualifications-list',views.EducationalQualificationList.as_view(), name='post'),
    path('update-educational-qualification',views.UpdateEducationalQualification.as_view(), name='post'),
    path('delete-educational-qualification',views.DeleteEducationalQualification.as_view(), name='post'),
    path('change-educational-qualification-status',views.ChangeEducationalQualificationStatus.as_view(), name='post'),


   



]