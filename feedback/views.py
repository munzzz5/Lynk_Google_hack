import json
import re
from .models import Feedback  # Adjust 'myapp' to your actual app name
from .models import User
import pandas as pd
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render
from .models import Summarised_Feedback
# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from feedback.forms import FeedbackForm
from .models import Feedback
from django.urls import reverse
from django.contrib.auth.decorators import login_required

import pandas as pd


def init_model():
    import pathlib
    import textwrap
    import google.generativeai as genai
    api_key = 'AIzaSyDukMqqjIFaEUt3fmM5iKm8QEKlN4CvThI'

    genai.configure(api_key=api_key)

    # Set up the model
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    return model


@login_required
def feedback_home(request):
    all_feedback = Feedback.objects.all()
    return render(request, 'feedback/feedback_home.html', {'feedbacks': all_feedback})
    # return render(request, 'feedback/feedback_home.html')


@login_required
def reset_step(request):
    request.session['feedback_step'] = 1  # Reset the session variable to 1
    # Replace 'step_1' with your first step's URL name
    return redirect('create_feedback')


@login_required
def feedback_flow(request):

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            load_tags = get_tags(form.cleaned_data['topic']+" "+form.cleaned_data['description'] +
                                 " "+form.cleaned_data['suggestions']+" "+form.cleaned_data['effect'])

            form.save()

            return redirect('feedback/feedback_form.html', {'form': form, 'tags': load_tags})
    else:
        form = FeedbackForm()
    return render(request, 'feedback/feedback_form.html', {'form': form})


# @login_required
# def feedback_flow(request):
#     step = request.session.get('feedback_step', 1)
#     feedback_data = request.session.get('feedback_data', {})

#     if request.method == 'POST':
#         if step == 1:
#             # Handle category selection
#             category = request.POST.get('category')
#             feedback_data['category'] = category
#             if category == 'work':
#                 request.session['feedback_step'] = 2
#             # Assuming 'personal' skips to the end or a different flow
#             # Adjust logic based on your actual flow requirements
#         elif step == 2:
#             # Handle topic and department
#             feedback_data['topic'] = request.POST.get('topic')
#             feedback_data['department'] = request.POST.get('department')
#             request.session['feedback_step'] = 3
#         elif step == 3:
#             # Final step: gather remaining data and save
#             feedback_data.update({
#                 'suggestions': request.POST.get('suggestions', ''),
#                 'effect': request.POST.get('effect', ''),
#                 # Assuming this is for problem/pain point
#                 'description': request.POST.get('description', ''),
#                 'tools': request.POST.get('tools', ''),
#                 'affected_areas': request.POST.get('affected_areas', ''),
#                 'user': request.user.id if not request.POST.get('anonymous', False) else None
#             })

#             # Create feedback object and clear session data
#             Feedback.objects.create(**feedback_data)
#             del request.session['feedback_step']
#             del request.session['feedback_data']
#             return redirect('feedback_success')  # Redirect to a success page

#     # else:
#     #     # For GET request, start or continue the flow based on step
#     #     if step > 1:
#     #         request.session['feedback_data'] = feedback_data

#     return render(request, f'feedback/step_{step}.html', {'feedback_data': feedback_data})


@login_required
def list_feedback(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'feedback/feedback_list.html', {'feedbacks': feedbacks})


@login_required
def detail_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    return render(request, 'feedback/feedback_detail.html', {'feedback': feedback})


@login_required
def feedback_edit(request, pk=None):
    if pk:
        feedback = get_object_or_404(Feedback, pk=pk)
    else:
        feedback = None

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            # Redirect to the feedback list view
            return redirect('feedback_list')
    else:
        form = FeedbackForm(instance=feedback)

    return render(request, 'feedback/edit_form.html', {'form': form})


def delete_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    if request.method == 'POST':
        feedback.delete()
        return redirect('list_feedback')
    return render(request, 'feedback/feedback_confirm_delete.html', {'feedback': feedback})


def get_feedback(request):
    feedback = Feedback.objects.all()
    return render(request, 'feedback/feedback_list.html', {'feedback': feedback})

# Tag generation


def auto_tag_model(text):
    prompt_tag = '''
        You are creating Automated tagging of the data:
        \nInstructions:
        \n1. Identify and extract the most relevant tags, keywords, or categories for the given data. These tags should succinctly represent the content's main themes, subjects, or topics.
        \n2. Consider the context, content, and domain-specific knowledge when selecting tags. Ensure that the tags accurately reflect the essence of the data.
        \n3. Ensure that your automated tagging results are unique, clear, relevant, and make the data more accessible and useful.
        \n4. Return top 10 frequent, relevant tags.
        \n5. Output the list of tags in the format: tag1, tag2, ... Follow this format strictly
        \n6. Do not respond with your own suggestions or recommendations or feedback.
        \ndata:\n\n'''
    input_string = prompt_tag + text
    model = init_model()
    response = model.generate_content(input_string)

    return response.text


def get_tags(form_data):
    # print(count_of_responses, "-------------------")
    # input_topic = concatenate_info(topic_to_summarise)
    tags = auto_tag_model(form_data)
    tags_list = [tags.lower() for tags in tags.split(", ")]

    return tags_list


###
# def format_response(response):
#     json_data = markdown_to_json(response)
#     return json_data

# # Print the JSON data
#     import json
#     print(json.dumps(json_data, indent=2, ensure_ascii=False))


def markdown_to_json(text):
    # Split the text into sections

    # Since the provided text seems to already be in JSON format (except for the possible presence of newline characters and the need to handle multiple JSON objects), we'll treat it as such.
    # Remove leading/trailing whitespaces and newline characters, and split the string into individual JSON objects if necessary.
    cleaned_text = text.strip().replace(
        '\n', '').replace('```', '').replace('json', '')
    # Attempt to parse the text as JSON directly (assuming it's a single JSON object or a list of JSON objects)
    try:
        data = json.loads(cleaned_text)
        return data
    except json.JSONDecodeError as e:
        print(f"Error parsing text: {e}")
        return None


def concatenate_info(group):
    concatenated_info = []
    for i, row in enumerate(group.itertuples(), 1):
        info = f"{i}. Description: {row.description}, Effect: {row.effect}, Suggestions: {row.suggestions}"
        concatenated_info.append(info)
    return ' | '.join(concatenated_info)


def get_response_model(topic_to_summarise):
    model = init_model()
    prompt_summarization = '''
  Based on a compilation of feedback from employees in an organization, including suggestions, complaints, pain points, and proposed improvements, generate a concise and professional report intended for senior management. The report should strictly adhere to the following structure and guidelines, presented in markdown format:

- **Format**: JSON
- Exactly three JSON keys, detailed as follows:
  1. **Topic**: Identify a single, overarching topic that encapsulates the majority of the feedback. Provide a brief description of this topic, focusing on the general subject area of the report.
  2. **Problem Summary**: Offer a concise summary of the principal issues or challenges associated with the chosen topic. Highlight key points to capture the scope and impact of these problems, ensuring the summary is informative and based strictly on the employee feedback.
  3. **Proposed Solutions**: Suggest practical strategies or actions to address the identified issues. Elaborate on the implementation of these solutions and discuss the expected outcomes or benefits.

- **Content Guidelines**:
  - The report must be devoid of sexually explicit content, hate speech, and offensive words.
  - Maintain a professional tone throughout the report.
  - Ensure clarity, organization, and comprehensiveness in covering all necessary aspects under each section.

Please include bullet points for clarity and ease of reading, ensuring the information is accurately distilled from the provided employee feedback.\n
  '''
    all_feedback = Feedback.objects.all()
    df_all_feedback = pd.DataFrame(list(all_feedback.values()))
    grouped_feedback = df_all_feedback.groupby('topic')

    selected_topic = grouped_feedback.get_group(topic_to_summarise)
    count_of_responses = selected_topic.shape[0]
    print(count_of_responses, "-------------------")
    input_topic = concatenate_info(selected_topic)

    response = model.generate_content(
        prompt_summarization + input_topic)
    print(response.text)
    return markdown_to_json(response.text)
    # to_markdown(response.text)


# print(get_response_model("Hygiene at the Workplace"))


def update_summarised_feedback():

    for topic in ['Growth Opportunities for Employees', 'Hygiene at the Workplace', 'Improvement in Product Application', 'Infrastructure Related', 'Team Collaboration Issues']:
        json_response = get_response_model(topic)
        print(json_response.keys())
        # print(json_response['Problem Summary'], json_response['Proposed Solutions'], json_response['Topic'])
        object_new = Summarised_Feedback(
            topic=topic, ai_topic=json_response['Topic'], ai_problem=json_response['Problem Summary'], ai_solution=json_response['Proposed Solutions'])
        object_new.save()


text_test = '''```json
{
  "Topic": "Mobile Car Rental App User Experience and Stability Enhancements",

  "Problem Summary": "- Inconsistent user experience across different devices due to lack of responsiveness.
- High dropout rate during checkout process due to complexity.
- Insufficient logging hinders timely issue diagnosis and resolution.
- Unintuitive user interface for managing bookings, affecting older users.
- Broad search functionality makes it difficult to find specific cars.
- Frequent app crashes during payment process frustrate users and lead to abandoned transactions.
- Poor discoverability of car rental extension feature.",

  "Proposed Solutions": "- Adopt a mobile-first design approach and utilize a responsive design framework.
- Simplify checkout process with fewer steps and clearer instructions.
- Enhance logging system to include detailed error messages and context.
- Conduct user interface redesign with focus on simplicity and usability, especially for older users.
- Refine search feature with more specific filters to improve user experience and reduce abandoned searches.
- Prioritize debugging of payment process and implement robust error handling mechanism.
- Redesign user interface to make extension feature more prominent and accessible from main menu."
}
```'''
# print(markdown_to_json(text_test)['Problem Summary'])

# update_summarised_feedback()

# # ####

# # # Load the Excel file
# # # excel_path = 'FeedBack.xlsx'

# # # Mapping function for category and department to their database values


# def map_category(value):
#     return {
#         'Work Related': 'work_related',
#         'Culture Related': 'culture_related',
#     }.get(value, 'other')  # default to 'other' if no match


# def map_department(value):
#     mapping = {
#         'IT': 'it',
#         'Human Resources': 'hr',
#         'Finance': 'finance',
#         'Marketing': 'marketing',
#         'Office Supplies': 'office supplies',
#         'Sales': 'sales',
#         'Other': 'other',
#         # Add mappings for other departments as necessary
#     }
#     return mapping.get(value, 'other')  # default to 'other' if no match

# # Assume we are uploading all feedback as a specific admin user or handle user differently as needed
# # user = User.objects.get(username='admin_username')


# def bulk_upload():
#     df = pd.read_excel("FeedBack (1).xlsx")

#     feedback_list = []
#     for index, row in df.iterrows():
#         feedback_list.append(Feedback(
#             category=map_category(row['Category']),
#             topic=row['Topic'],
#             department=map_department(row['Department']),
#             description=row['Description'],
#             effect=row['Effect'] if not pd.isna(row['Effect']) else '',
#             suggestions=row['Suggestions'] if not pd.isna(
#                 row['Suggestions']) else '',
#             tools=row['Tools'] if not pd.isna(row['Tools']) else '',
#             affected_areas=row['Affected Areas'] if not pd.isna(
#                 row['Affected Areas']) else '',
#             tags=row['tags'] if not pd.isna(row['tags']) else '',
#             subtopic=row['Sub topic'] if not pd.isna(row['Sub topic']) else '',
#             # Uncomment and adjust if linking feedback to a user
#             user=User.objects.get(email="abhanda2@andrew.cmu.edu"),
#         ))

#     # Bulk create the feedback instances
#     Feedback.objects.bulk_create(feedback_list)

#     print(f"{len(feedback_list)} feedback instances created successfully.")


# bulk_upload()
