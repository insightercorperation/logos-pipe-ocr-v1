import unittest
import os
from logos_pipe_ocr.util.dataloaders import EvalDataLoader

class TestEvalDataLoader(unittest.TestCase):
    def setUp(self):
        """테스트를 위한 초기 설정."""
        self.label_dir = 'test_dir/label'  # 테스트 레이블 디렉토리
        self.output_dir = 'test_dir/output'  # 테스트 출력 디렉토리
        
        # 테스트 디렉토리 및 파일 생성
        os.makedirs(self.label_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 테스트 레이블 파일 생성
        with open(os.path.join(self.label_dir, 'label1.json'), 'w') as f:
            f.write('{}')
        with open(os.path.join(self.label_dir, 'label2.json'), 'w') as f:
            f.write('{}')
        
        # 테스트 출력 파일 생성
        with open(os.path.join(self.output_dir, 'label1.json'), 'w') as f:
            f.write('output1')
        
    def tearDown(self):
        """테스트 후 정리 작업."""
        # 생성된 파일 및 디렉토리 삭제
        for dir_path in [self.label_dir, self.output_dir]:
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    os.remove(os.path.join(dir_path, file))
                os.rmdir(dir_path)
        # test_dir 삭제
        if os.path.exists('test_dir'):
            os.rmdir('test_dir')  # test_dir 삭제

    def test_eval_data_loader(self):
        """EvalDataLoader의 기본 기능 테스트."""
        loader = EvalDataLoader(self.label_dir, self.output_dir)
        self.assertEqual(len(loader), 1)  # 레이블 파일과 출력 파일이 하나만 있어야 함
        
        label_paths = loader.get_label_file_paths()
        output_paths = loader.get_output_file_paths()
        
        self.assertEqual(len(label_paths), len(output_paths))  # 레이블 파일과 출력 파일이 쌍으로 존재해야 함
        self.assertIn(os.path.join(self.label_dir, 'label1.json'), label_paths)
        self.assertIn(os.path.join(self.output_dir, 'label1.json'), output_paths)

if __name__ == '__main__':
    unittest.main() 