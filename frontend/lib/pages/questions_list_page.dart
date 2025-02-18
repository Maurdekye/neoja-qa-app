import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../models/question.dart';
import '../widgets/questions_list_widget.dart';
import 'question_submission_page.dart';
import '../widgets/category_filter_panel.dart';

class QuestionsListPage extends StatefulWidget {
  @override
  _QuestionsListPageState createState() => _QuestionsListPageState();
}

class _QuestionsListPageState extends State<QuestionsListPage> {
  List<Question> _questions = [];
  List<String> _categories = ['All'];
  String _selectedCategory = 'All';
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _fetchQuestions();
  }

  Future<void> _fetchQuestions() async {
    setState(() => _loading = true);
    final apiService = Provider.of<APIService>(context, listen: false);
    try {
      final data = await apiService.fetchQuestions();
      // Extract distinct categories from fetched questions
      final fetchedCategories = data.map((q) => q.category).toSet().toList();
      setState(() {
        _questions = data;
        _categories = ['All', ...fetchedCategories];
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
      print('Error fetching questions: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    // Filter questions based on selected category
    final filteredQuestions = _selectedCategory == 'All'
        ? _questions
        : _questions.where((q) => q.category == _selectedCategory).toList();

    return Scaffold(
      appBar: AppBar(title: Text('Neoja Q&A App')),
      body: Column(
        children: [
          CategoryFilterPanel(
            selectedCategory: _selectedCategory,
            categories: _categories,
            onChanged: (newCategory) {
              setState(() {
                _selectedCategory = newCategory;
              });
            },
          ),
          Expanded(
            child: _loading
                ? Center(child: CircularProgressIndicator())
                : QuestionsListWidget(questions: filteredQuestions),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => QuestionSubmissionPage(),
            ),
          );
          if (result == true) {
            // Refetch questions if a new one was created
            _fetchQuestions();
          }
        },
        child: Icon(Icons.add),
      ),
    );
  }
}
