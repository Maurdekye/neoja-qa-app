import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';

class QuestionsListPage extends StatefulWidget {
  @override
  _QuestionsListPageState createState() => _QuestionsListPageState();
}

class _QuestionsListPageState extends State<QuestionsListPage> {
  List<dynamic> _questions = [];
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
      setState(() {
        _questions = data;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
      print('Error fetching questions: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Q&A App')),
      body: _loading
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: _questions.length,
              itemBuilder: (context, index) {
                final question = _questions[index];
                return ListTile(
                  title: Text(question['title'] ?? 'No title'),
                  subtitle: Text(question['_id'] ?? ''),
                  onTap: () {
                    Navigator.pushNamed(
                      context,
                      '/questionDetail',
                      arguments: question['_id'],
                    );
                  },
                );
              },
            ),
    );
  }
}
